import traceback
try:
    import backend.main
    from backend.main import create_initial_data
    create_initial_data()
    print("Success")
except Exception as e:
    with open("trace.txt", "w") as f:
        f.write(traceback.format_exc())
