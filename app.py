from flask import Flask, render_template, request
import base64
import io
import math
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)


def get_first_digit(value):
    """Return the first non-zero digit from a numeric string."""
    if pd.isna(value):
        return None

    s = str(value).strip()
    s = s.replace(",", "").replace("%", "")

    if s.startswith("-"):
        s = s[1:]

    s = s.replace(".", "")
    s = s.lstrip("0")

    if s == "" or not s[0].isdigit():
        return None

    first = int(s[0])
    return first if first != 0 else None


def analyze_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        return None, f"CSV 讀取失敗：{exc}"

    if df.empty:
        return None, "CSV 檔沒有資料"

    # Prefer an obvious close/price column; fall back to last column.
    close_col = None
    for col in df.columns:
        col_name = str(col).lower()
        if "收盤" in str(col) or "close" in col_name or "price" in col_name:
            close_col = col
            break

    if close_col is None:
        close_col = df.columns[-1]

    values = []
    for item in df[close_col]:
        d = get_first_digit(item)
        if d is not None:
            values.append(d)

    if not values:
        return None, "找不到可分析的收盤價資料"

    counts = pd.Series(values).value_counts().reindex(range(1, 10), fill_value=0).sort_index()
    probabilities = counts / counts.sum()
    benford = [math.log10(1 + (1 / d)) for d in range(1, 10)]

    result_df = pd.DataFrame({
        "數字": list(range(1, 10)),
        "出現次數": counts.values,
        "實際比例(%)": (probabilities * 100).round(2),
        "班佛定律理論值(%)": (pd.Series(benford) * 100).round(2),
    })

    return result_df, None


def generate_chart(result_df):
    digits = result_df["數字"].astype(str)
    actual = result_df["實際比例(%)"]
    theory = result_df["班佛定律理論值(%)"]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = list(range(len(digits)))
    width = 0.35

    bars1 = ax.bar([i - width / 2 for i in x], actual, width, label="實際比例", color="#4C78A8", alpha=0.9)
    bars2 = ax.bar([i + width / 2 for i in x], theory, width, label="班佛定律理論值", color="#F58518", alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(digits)
    ax.set_xlabel("首位數字")
    ax.set_ylabel("比例 (%)")
    ax.set_title("首位數字分佈：實際 vs 班佛定律")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9)

    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded = request.files.get("csv_file")
        if uploaded is None or uploaded.filename == "":
            return render_template("index.html", error="請先選擇 CSV 檔案")

        result_df, error = analyze_csv(uploaded)
        if error:
            return render_template("index.html", error=error)

        chart_b64 = generate_chart(result_df)
        return render_template(
            "index.html",
            table_html=result_df.to_html(index=False, classes="table table-striped"),
            chart_data=chart_b64,
            total_count=int(result_df["出現次數"].sum()),
            error=None,
        )

    return render_template("index.html", error=None)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
