"""Define a MockS3Client class that simulates an S3 client."""


class MockS3Client:
    """Provide a minimal interface to the S3 client for backtesting."""

    def download_file(*args, **kwargs) -> None:
        """Do nothing."""
        pass
