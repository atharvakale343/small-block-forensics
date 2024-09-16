import hashlib
import mmap
import os
import random
import sqlite3
from math import prod
from pathlib import Path
from typing import List, Tuple

from small_blk_forensics.utils.data import ModelResponse


def prod_prob(n_samples, blocks_of_known_content, total_blocks_to_scan):
    C, N = blocks_of_known_content, total_blocks_to_scan
    return prod(((N - (i - 1)) - C) / (N - (i - 1)) for i in range(1, n_samples + 1))


class SmallBlockForensicsModel:
    def __init__(self, block_size: int = 4096, target_probability: float = 1):
        self.block_size = block_size
        self.target_probability = target_probability
        self.num_hashed_blocks = 0  # will be set at runtime
        self.num_random_blocks = (
            0  # will be set at runtime based on number of blocks in target and known directory
        )

    def _calculate_num_random_blocks(self, blocks_of_known_content, blocks_in_target) -> int:
        """Find the minimum number of samples where the probability < threshold."""
        if self.target_probability == 1:
            return blocks_in_target
        lo, hi = 0, blocks_in_target

        while lo <= hi:
            mid = (lo + hi) // 2
            probability = prod_prob(mid, blocks_of_known_content, blocks_in_target)

            if probability <= 1 - self.target_probability:
                # Continue searching in the lower half to find the minimum n_samples
                hi = mid - 1
            else:
                # Probability is too high, search in the upper half
                lo = mid + 1

        return lo  # At the end, lo will be the smallest n_samples where probability < threshold

    def _hash_block(self, block: bytes) -> str:
        """
        Computes the MD5 hash of a given block.
        """
        return hashlib.md5(block).hexdigest()

    def _store_hash_in_db(
        self, block_num: int, hash_value: str, file_path: str, db_conn: sqlite3.Connection
    ) -> None:
        """
        Store the computed hash along with the file path in an SQLite database.
        """
        c = db_conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS hashes (
            hash TEXT PRIMARY KEY,
            file_path TEXT,
            block_num INTEGER UNIQUE
        )"""
        )
        c.execute(
            "INSERT OR IGNORE INTO hashes (hash, file_path, block_num) VALUES (?, ?, ?)",
            (hash_value, file_path, block_num),
        )

        db_conn.commit()

    def _query_hash_in_db(self, target_hash: str, db_conn: sqlite3.Connection) -> Tuple[bool, str, int]:
        """
        Query the SQLite database to check if a given target hash exists.
        Returns a tuple of (found: bool, file_path: str, block_num: int).
        """
        c = db_conn.cursor()
        c.execute("SELECT file_path, block_num FROM hashes WHERE hash = ?", (target_hash,))
        result = c.fetchone()
        if result:
            return True, result[0], result[1]
        return False, "", -1

    def _get_number_of_hashed_blocks(self, db_conn: sqlite3.Connection) -> int:
        """
        Query the SQLite database to check if a given target hash exists.
        Returns a tuple of (found: bool, file_path: str, block_num: int).
        """
        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM hashes")
        result = c.fetchone()
        return result[0]

    def _get_all_blocks_from_file(self, file_path: Path, db_conn: sqlite3.Connection) -> None:
        """
        Hash all blocks from a given file and store the hashes and file paths in the database.
        """
        file_size = os.path.getsize(file_path)
        num_blocks = (file_size + self.block_size - 1) // self.block_size

        if file_size == 0:
            return

        with open(file_path, "rb") as f:
            mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

            for block_num in range(num_blocks):
                mmapped_file.seek(block_num * self.block_size)
                block = mmapped_file.read(self.block_size)

                block_hash = self._hash_block(block)
                self._store_hash_in_db(block_num, block_hash, str(file_path), db_conn)

            mmapped_file.close()

    def _get_random_blocks_from_file(
        self, file_path: Path, random_blocks: List[int], db_conn: sqlite3.Connection
    ) -> Tuple[bool, str, int, int]:
        """
        Given a file and a list of random block offsets, hash those blocks and check the DB for matches.
        If a match is found, return immediately with the True, file path, block_num_in_target, block_num_in_known_content
        """
        file_size = os.path.getsize(file_path)

        if file_size == 0:
            return False, "", -1, -1

        num_blocks = (file_size + self.block_size - 1) // self.block_size  # Total blocks in the file

        with open(file_path, "rb") as f:
            # Use memory-mapping for efficiency
            mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

            for block_num in random_blocks:
                if block_num >= num_blocks:
                    continue  # Skip if the block number exceeds the total blocks in this file

                # Move to the start of the block
                mmapped_file.seek(block_num * self.block_size)

                # Read the block and hash it
                block = mmapped_file.read(self.block_size)
                block_hash = self._hash_block(block)

                # Check if this hash exists in the known content database
                found, known_file_path, block_num_in_known_content = self._query_hash_in_db(
                    block_hash, db_conn
                )
                if found:
                    # Return the match immediately if found
                    return True, known_file_path, block_num, block_num_in_known_content

            mmapped_file.close()

        return False, "", -1, -1

    def _generate_file_block_map(self, directory: Path) -> Tuple[List[Tuple[Path, int]], int]:
        file_block_map = []
        total_blocks = 0

        # Calculate total number of blocks in all files
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    continue
                num_blocks_in_file = (file_size + self.block_size - 1) // self.block_size
                file_block_map.append((file_path, num_blocks_in_file))
                total_blocks += num_blocks_in_file

        # Set the number of blocks parameter
        self.num_random_blocks = self._calculate_num_random_blocks(self.num_hashed_blocks, total_blocks)

        return file_block_map, total_blocks

    def _select_random_blocks(self, directory: Path) -> List[Tuple[Path, List[int]]]:
        """
        Select random blocks from all files in the directory.
        Returns a list of tuples (file_path, block_indices).
        """
        file_block_map, total_blocks = self._generate_file_block_map(directory)

        # Ensure we don't try to select more blocks than exist
        num_blocks_to_select = min(self.num_random_blocks, total_blocks)

        # Select random blocks globally across all files
        random_block_indices = sorted(random.sample(range(total_blocks), num_blocks_to_select))

        selected_blocks = []
        current_block_index = 0

        # Distribute random block indices across files
        for file_path, num_blocks_in_file in file_block_map:
            block_indices = []
            while (
                current_block_index < len(random_block_indices)
                and random_block_indices[current_block_index] < num_blocks_in_file
            ):
                block_indices.append(random_block_indices[current_block_index])
                current_block_index += 1

            random_block_indices = [i - num_blocks_in_file for i in random_block_indices]  # Shift indices

            if block_indices:
                selected_blocks.append((file_path, block_indices))

        return selected_blocks

    def _hash_directory_random_blocks(self, directory: Path, db_conn: sqlite3.Connection) -> ModelResponse:
        """
        Hashes random blocks from all files in the directory, and checks the known content hashes in the DB.
        If a match is found, it returns immediately with the file path and hash.
        """
        random_blocks_info = self._select_random_blocks(directory)

        for file_path, random_blocks in random_blocks_info:
            found, known_file_path, block_num_in_target, block_num_in_known_dataset = (
                self._get_random_blocks_from_file(file_path, random_blocks, db_conn)
            )
            if found:
                return ModelResponse(
                    found=True,
                    target_file=str(file_path),
                    known_dataset_file=known_file_path,
                    block_num_in_target=block_num_in_target,
                    block_num_in_known_dataset=block_num_in_known_dataset,
                )

        return ModelResponse(found=False)

    def _hash_directory(self, directory: Path, db_conn: sqlite3.Connection) -> None:
        """
        Fully hashes all blocks of files in the given directory and stores the results in the database.
        """
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                self._get_all_blocks_from_file(file_path, db_conn)

    def _generate_db_filename(self, output_directory: Path):
        # return output_directory / f"known_content_hashes_{str(uuid4())[:8]}.sqlite"
        return output_directory / "known_content_hashes.sqlite"

    def _get_db_conn(self, db_path: Path):
        return sqlite3.connect(db_path)

    def run_with_known_content_directory(
        self, known_content_directory: Path, target_directory: Path, out_dir: Path
    ) -> ModelResponse:
        """
        Applies the small block technique to the known content directory and target directory.
        """
        db_path = self._generate_db_filename(out_dir)
        db_conn = self._get_db_conn(db_path)

        # Fully hash the known content directory and store hashes in the output directory's database
        self._hash_directory(known_content_directory, db_conn)
        print(f"INFO: Successfully processed {str(known_content_directory)} and stored hashes at {db_path}")

        # Set number of hashed blocks
        self.num_hashed_blocks = self._get_number_of_hashed_blocks(db_conn)

        # Hash the target directory and check for matches using random blocks
        response = self._hash_directory_random_blocks(target_directory, db_conn)

        return response

    def run_with_known_content_sqlite(
        self, known_content_sqlite: Path, target_directory: Path
    ) -> ModelResponse:
        """
        Applies the small block technique using known content from an SQLite database.
        """
        db_conn = self._get_db_conn(known_content_sqlite)

        # Set number of hashed blocks
        self.num_hashed_blocks = self._get_number_of_hashed_blocks(db_conn)

        # Hash the target directory and check for matches
        response = self._hash_directory_random_blocks(target_directory, db_conn)

        return response
