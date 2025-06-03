import sys
from chord_extraction import check_backend_availability

def main():
    print("Chord Extraction Backend Availability:")
    availability = check_backend_availability()
    for backend, available in availability.items():
        status = 'Available' if available else 'Unavailable'
        print(f"  {backend}: {status}")
    if not any(availability.values()):
        print("\nNo chord extraction backends available. See README for setup instructions.")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
