print("Safety Monitor module")
print("""
Select:
1) Run Safety monitor standalone
2) Run Safety monitor web server 
""")

while True:
    try:
        choice = int(input("Select: "))
    except Exception as e:
        print(f"Failed to choose {e}. Try again")
        continue

    if choice == 1:
        from .safety_monitor import main
        main()
    if choice == 2:
        import uvicorn
        from .monitor import app

        uvicorn.run(app, host="0.0.0.0", port=8000)
            
