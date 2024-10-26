import matplotlib.pyplot as plt
import requests
import datetime
import time

def fetch_data():
    try:
        response = requests.get("https://jiranek-chochola.cz/die-experts/index.php?limit=1")
        data = response.json()
        return data[-1]  # Get the latest data point
    except Exception as e:
        print("Error fetching data:", e)
        return None

def live_update_graph(ax):
    # Initial data lists
    x_data = []
    y_data = []

    # Plot initial empty line
    line, = ax.plot(x_data, y_data, label="Heart Rate", color="cyan")
    
    # Set axis limits and format
    #ax.set_ylim(60, 200)
    ax.xaxis_date()  # Format x-axis for timestamps

    # Set legend
    ax.legend(loc="upper right", fontsize=10)

    # Infinite loop for continuous data fetching and plotting
    while plt.fignum_exists(ax.get_figure().number):  # Check if plot window is open
        # Fetch new data from the API
        latest_data = fetch_data()
        if latest_data:
            # Parse the timestamp and heart rate
            heart_rate = float(latest_data['heartRate'])
            timestamp = datetime.datetime.fromtimestamp(int(latest_data['timestamp']))

            print(f"Timestamp: {timestamp}, Heart Rate: {heart_rate}")
            
            # Append the new data
            x_data.append(timestamp)
            y_data.append(heart_rate)
            
            # Keep only the last 50 points
            if len(x_data) > 50:
                x_data = x_data[-50:]
                y_data = y_data[-50:]
            
            # Update the line with new data
            line.set_xdata(x_data)
            line.set_ydata(y_data)
            
            # Adjust x-axis limits to show the latest 50 points
            ax.set_xlim(x_data[0], x_data[-1])
            ax.relim()
            ax.autoscale_view()
            
            # Redraw the plot
            plt.draw()
        
        # Pause briefly to simulate real-time data
        plt.pause(1)  # Update every second


