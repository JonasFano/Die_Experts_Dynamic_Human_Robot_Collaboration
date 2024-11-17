import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("Hello World Window")

# Set window size
window.geometry("300x200")

# Add a label
label = tk.Label(window, text="Hello, World!", font=("Arial", 16))
label.pack(expand=True)

# Run the application
window.mainloop()
