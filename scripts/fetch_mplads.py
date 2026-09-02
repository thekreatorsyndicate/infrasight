from src.ingestion.mplads_api import MPLADSClient


def main():
    client = MPLADSClient()

    client.initialize_session()

    data = client.fetch_report("Works Completed")

    print("\nSuccessfully fetched MPLADS data.")

    if isinstance(data, list):
        print("Records:", len(data))

        if data:
            print("\nFirst record:")
            print(data[0])
    else:
        print("Response type:", type(data))
        print("Response:")
        print(data)


if __name__ == "__main__":
    main()