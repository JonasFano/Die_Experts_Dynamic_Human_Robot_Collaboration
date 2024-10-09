import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from graph import live_update_graph  # Assuming this is already provided

# Load two sample images (replace these with your actual image paths)
image1_path = 'images/all_components.png'
image2_path = 'images/all_components.png'

# Helper function to display an image in a given axis with dark mode styling
def display_image(ax, image_path):
    img = plt.imread(image_path)
    ax.imshow(img)
    ax.axis('off')  # Hide axes for images
    ax.set_facecolor('#1E1E1E')  # Dark background for image panels

# Function to style the graph axes for dark mode
def style_ax_for_dark_mode(ax):
    # Set dark background
    ax.set_facecolor('#1E1E1E')

    # Customize the tick labels
    ax.tick_params(colors='white')  # Set the tick color to white
    ax.xaxis.label.set_color('white')  # X-axis label
    ax.yaxis.label.set_color('white')  # Y-axis label

    # Set the grid and label colors
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')

    ax.title.set_color('white')
    ax.grid(True, color='#2A2A2A')  # Set grid color

# Function to handle the grid layout with dark mode
def display_layout(image1_path, image2_path):
    # Set the figure background to dark
    fig = plt.figure(figsize=(10, 6), facecolor='#1E1E1E')  # Dark mode background

    # Create GridSpec layout (2x2 grid, graph spanning right two rows)
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 2], height_ratios=[1, 1])

    # Top-left: Image 1
    ax1 = fig.add_subplot(gs[0, 0])
    display_image(ax1, image1_path)

    # Bottom-left: Image 2
    ax2 = fig.add_subplot(gs[1, 0])
    display_image(ax2, image2_path)

    # Right column (spans both rows): Embed the graph in this space
    ax3 = fig.add_subplot(gs[:, 1])
    ax3.set_title("Live Graph", fontsize=12, color='white')  # Graph title in white
    style_ax_for_dark_mode(ax3)  # Apply dark mode styling to graph

    plt.tight_layout()

    # Run the live graph update inside the right column
    live_update_graph(ax3)

    # Keep the main UI running
    plt.show()

if __name__ == "__main__":
    # Display the layout with images and live graph embedded in the right column with dark mode
    display_layout(image1_path, image2_path)
