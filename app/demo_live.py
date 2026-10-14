
import subprocess


def ping_host(host: str) -> None:
    # DEMO ONLY: unsafe use of shell=True with external input
    subprocess.run(f"ping -c 1 {host}", shell=True)


if __name__ == "__main__":
    print("Demo file for AI vulnerability scanning.")
