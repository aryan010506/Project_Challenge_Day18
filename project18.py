import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sns.set_theme(style="whitegrid")

class IPLDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("IPL Dashboard - Aryan Sunil")
        self.root.geometry("1200x750")

        self.matches_df = None
        self.deliveries_df = None

        self.create_widgets()

    def create_widgets(self):
        # Top frame
        top_frame = tk.Frame(self.root, pady=5)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        load_matches_btn = tk.Button(top_frame, text="Load Matches CSV", command=self.load_matches)
        load_matches_btn.pack(side=tk.LEFT, padx=5)

        load_deliveries_btn = tk.Button(top_frame, text="Load Deliveries CSV", command=self.load_deliveries)
        load_deliveries_btn.pack(side=tk.LEFT, padx=5)

        # Dropdown filters
        self.season_var = tk.StringVar()
        self.team_var = tk.StringVar()

        tk.Label(top_frame, text="Filter Season:").pack(side=tk.LEFT, padx=5)
        self.season_cb = ttk.Combobox(top_frame, textvariable=self.season_var, width=10, state="readonly")
        self.season_cb.pack(side=tk.LEFT)

        tk.Label(top_frame, text="Filter Team:").pack(side=tk.LEFT, padx=5)
        self.team_cb = ttk.Combobox(top_frame, textvariable=self.team_var, width=20, state="readonly")
        self.team_cb.pack(side=tk.LEFT)

        apply_btn = tk.Button(top_frame, text="Apply Filters", command=self.update_charts)
        apply_btn.pack(side=tk.LEFT, padx=5)

        # Notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.frames = {}
        for name in ["Matches per Season", "Team Wins", "Toss vs Win", "Top Batsmen", "Top Bowlers", "Venues"]:
            frame = tk.Frame(self.notebook)
            frame.pack(fill=tk.BOTH, expand=True)
            self.notebook.add(frame, text=name)
            self.frames[name] = frame

        self.figures = {name: plt.Figure(figsize=(5, 4), dpi=100) for name in self.frames}
        self.canvases = {}
        for name, frame in self.frames.items():
            canvas = FigureCanvasTkAgg(self.figures[name], master=frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.canvases[name] = canvas

    def load_matches(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        self.matches_df = pd.read_csv(file_path)

        # Fill dropdowns
        seasons = sorted(self.matches_df['season'].unique())
        self.season_cb['values'] = ['All'] + list(seasons)
        self.season_cb.set('All')
        teams = sorted(set(self.matches_df['team1']).union(set(self.matches_df['team2'])))
        self.team_cb['values'] = ['All'] + list(teams)
        self.team_cb.set('All')
        messagebox.showinfo("Loaded", "Matches CSV loaded successfully!")
        self.update_charts()

    def load_deliveries(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        self.deliveries_df = pd.read_csv(file_path)
        messagebox.showinfo("Loaded", "Deliveries CSV loaded successfully!")
        self.update_charts()

    def apply_filters(self):
        df = self.matches_df.copy()
        if self.season_var.get() != 'All':
            df = df[df['season'] == int(self.season_var.get())]
        if self.team_var.get() != 'All':
            df = df[(df['team1'] == self.team_var.get()) | (df['team2'] == self.team_var.get())]
        return df

    def update_charts(self):
        if self.matches_df is None:
            return

        df = self.apply_filters()

        # 1. Matches per Season
        ax1 = self.figures["Matches per Season"].clear()
        ax1 = self.figures["Matches per Season"].add_subplot(111)
        season_counts = df['season'].value_counts().sort_index()
        sns.barplot(x=season_counts.index, y=season_counts.values, ax=ax1, palette="viridis")
        ax1.set_title("Matches per Season")
        ax1.set_xlabel("Season")
        ax1.set_ylabel("Matches")
        self.canvases["Matches per Season"].draw()

        # 2. Team Wins
        ax2 = self.figures["Team Wins"].clear()
        ax2 = self.figures["Team Wins"].add_subplot(111)
        team_wins = df['winner'].value_counts().head(10)
        sns.barplot(x=team_wins.values, y=team_wins.index, ax=ax2, palette="plasma")
        ax2.set_title("Top 10 Teams by Wins")
        ax2.set_xlabel("Wins")
        ax2.set_ylabel("Team")
        self.canvases["Team Wins"].draw()

        # 3. Toss vs Win
        ax3 = self.figures["Toss vs Win"].clear()
        ax3 = self.figures["Toss vs Win"].add_subplot(111)
        toss_win_df = df[df['toss_winner'] == df['winner']]
        toss_lost_df = df[df['toss_winner'] != df['winner']]
        toss_counts = pd.Series({
            'Won Toss & Won Match': len(toss_win_df),
            'Won Toss but Lost Match': len(toss_lost_df)
        })
        sns.barplot(x=toss_counts.values, y=toss_counts.index, ax=ax3, palette="coolwarm")
        ax3.set_title("Toss vs Match Result")
        ax3.set_xlabel("Matches")
        self.canvases["Toss vs Win"].draw()

        # If deliveries available → Top Batsmen & Bowlers
        if self.deliveries_df is not None:
            match_ids = df['id']  # ensures filtered matches only
            deliveries_filtered = self.deliveries_df[self.deliveries_df['match_id'].isin(match_ids)]

            # 4. Top Batsmen
            batsmen_runs = deliveries_filtered.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(10)
            ax4 = self.figures["Top Batsmen"].clear()
            ax4 = self.figures["Top Batsmen"].add_subplot(111)
            sns.barplot(x=batsmen_runs.values, y=batsmen_runs.index, ax=ax4, palette="magma")
            ax4.set_title("Top 10 Batsmen (Runs)")
            ax4.set_xlabel("Runs")
            ax4.set_ylabel("Batsman")
            self.canvases["Top Batsmen"].draw()

            # 5. Top Bowlers
            wickets = deliveries_filtered[deliveries_filtered['dismissal_kind'].notnull()]
            bowler_wickets = wickets.groupby('bowler').size().sort_values(ascending=False).head(10)
            ax5 = self.figures["Top Bowlers"].clear()
            ax5 = self.figures["Top Bowlers"].add_subplot(111)
            sns.barplot(x=bowler_wickets.values, y=bowler_wickets.index, ax=ax5, palette="cool")
            ax5.set_title("Top 10 Bowlers (Wickets)")
            ax5.set_xlabel("Wickets")
            ax5.set_ylabel("Bowler")
            self.canvases["Top Bowlers"].draw()

        # 6. Venues
        ax6 = self.figures["Venues"].clear()
        ax6 = self.figures["Venues"].add_subplot(111)
        venue_counts = df['venue'].value_counts().head(10)
        sns.barplot(x=venue_counts.values, y=venue_counts.index, ax=ax6, palette="cubehelix")
        ax6.set_title("Top Venues (Matches)")
        ax6.set_xlabel("Matches")
        ax6.set_ylabel("Venue")
        self.canvases["Venues"].draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = IPLDashboard(root)
    root.mainloop()
