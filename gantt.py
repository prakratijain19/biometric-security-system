import matplotlib.pyplot as plt

# --- Data for the Project Plan ---
# Define the phases of the project in the desired order
phases = [
    'Req Analysis',
    'System Design',
    'Development',
    'Testing',
    'Deployment',
    'Maintenance'
]

# Define the average duration in weeks for plotting the bar lengths
# For "Ongoing", we'll use a value that extends to the end of the chart
durations = [2.5, 3.5, 10, 3.5, 1.5, 12]

# Define the text labels to display next to each bar
duration_labels = [
    '2-3w',
    '3-4w',
    '8-12w',
    '3-4w',
    '1-2w',
    'Ongoing'
]

# Define colors for each bar to match the reference image's style
colors = [
    '#00BCD4',  # Cyan
    '#F44336',  # Red
    '#4CAF50',  # Green
    '#607D8B',  # Blue Grey
    '#FFEB3B',  # Yellow
    '#D32F2F'   # Darker Red
]

# --- Create the Plot ---
# Set the figure size for better readability
plt.figure(figsize=(10, 6))

# Create the horizontal bar chart
bars = plt.barh(phases, durations, color=colors)

# Invert the Y-axis so 'Req Analysis' is at the top
plt.gca().invert_yaxis()

# --- Customize the Chart's Appearance ---
# Add a title and labels for the axes
plt.title('SW Project Plan Phases', fontsize=16)
plt.xlabel('Duration (wks)', fontsize=12)
plt.ylabel('Phase Sequence', fontsize=12)

# Set the x-axis limits to give space for labels
plt.xlim(0, 13)

# Add faint vertical grid lines for better readability
plt.grid(axis='x', linestyle='--', alpha=0.6)

# Add the duration labels next to each bar
for index, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 0.1,  # x position (just after the bar)
             bar.get_y() + bar.get_height() / 2,  # y position (centered on the bar)
             duration_labels[index],  # The text label
             va='center')  # Vertically align text to the center

# Ensure the layout is clean and labels don't overlap
plt.tight_layout()

# --- Display the Chart ---
# Show the generated plot in a new window
plt.show()
