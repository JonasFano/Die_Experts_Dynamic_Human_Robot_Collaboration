# graph.py
import matplotlib.pyplot as plt
import numpy as np
import datetime

def live_update_graph(ax):
    # Create initial data for both data sets
    x_data = []
    y_data1 = []
    y_data2 = []

    # Plot initial empty lines for both data sets
    line1, = ax.plot(x_data, y_data1, label="Data Set 1", color="cyan")
    line2, = ax.plot(x_data, y_data2, label="Data Set 2", color="magenta")
    
    # Set axis limits and format
    ax.set_ylim(60, 200)
    ax.xaxis_date()  # Formatting the x-axis to display timestamps nicely

    # Add the legend (this will allow toggling visibility)
    legend = ax.legend(loc="upper right", fontsize=10)

    # Increase the size of the lines in the legend for better visibility
    for legend_line in legend.get_lines():
        legend_line.set_linewidth(8.0)  # Set legend line width

    
    # Set up the event handler for clicking on the legend to toggle visibility
    lines = [line1, line2]
    def on_pick(event):
        legend_line = event.artist
        orig_visibility = legend_line.get_visible()
        legend_line.set_visible(not orig_visibility)
        for legline, origline in zip(legend.get_lines(), lines):
            if legline == legend_line:
                origline.set_visible(not orig_visibility)
        plt.draw()

    fig = ax.get_figure()
    fig.canvas.mpl_connect('pick_event', on_pick)

    for legline in legend.get_lines():
        legline.set_picker(True)  # Enable legend line picking

    # Start with initial values in the range
    current_value1 = np.random.uniform(60, 110)  # Initial value for first data set
    current_value2 = np.random.uniform(100, 150)  # Initial value for second data set

    # Infinite loop for continuous data generation
    while plt.fignum_exists(fig.number):  # Check if the plot window is open
        # Simulate new data by adding a small variation to both data sets
        variation1 = np.random.uniform(-5, 5)  # Small variation for first data set
        variation2 = np.random.uniform(-7, 7)  # Small variation for second data set

        current_value1 = np.clip(current_value1 + variation1, 60, 200)
        current_value2 = np.clip(current_value2 + variation2, 60, 200)
        
        # Append the new data
        current_time = datetime.datetime.now()
        x_data.append(current_time)
        y_data1.append(current_value1)
        y_data2.append(current_value2)
        
        # Keep only the last 50 points
        if len(x_data) > 50:
            x_data = x_data[-50:]
            y_data1 = y_data1[-50:]
            y_data2 = y_data2[-50:]
        
        # Update the lines with new data
        line1.set_xdata(x_data)
        line2.set_xdata(x_data)
        line1.set_ydata(y_data1)
        line2.set_ydata(y_data2)
        
        # Adjust limits if necessary
        ax.set_xlim(x_data[0], x_data[-1])  # Dynamically adjust x-axis to keep 50 points visible
        ax.relim()
        ax.autoscale_view()
        
        # Redraw the plot
        plt.draw()
        
        # Pause briefly to simulate real-time data
        plt.pause(0.05)
