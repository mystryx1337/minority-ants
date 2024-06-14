import plot

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    """
    Starts the Software with a default configuration
    """
    try:
        AcoPlotObj = plot.Plot('configurations/minority_2d_grid_torus.json')
    except:
        try:
            # Pycharm
            print("loading pycharm")
            AcoPlotObj = plot.Plot('../configurations/minority_2d_grid_torus.json')
        except Exception as e:
            print(f"Error loading config from PyCharm path: {e}. Loading default values.")
            AcoPlotObj = plot.Plot(None)
