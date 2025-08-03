from django.shortcuts import render

# Create your views here.
# views.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from User.models import *  # Replace with your actual model

def analyze_sentiment(review):
    analysis = TextBlob(review)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'
@csrf_exempt
def homepage(request):
    if request.method == 'POST':
        # Fetch data from the database
        reviews = tbl_review.objects.all().values('review')
        df = pd.DataFrame(list(reviews))

        # Perform sentiment analysis
        df['sentiment'] = df['review'].apply(analyze_sentiment)
        sentiment_counts = df['sentiment'].value_counts()

        # Create a figure with a 2x2 grid
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # Bar chart
        sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette='viridis', ax=axes[0, 0])
        axes[0, 0].set_title('Sentiment Distribution')
        axes[0, 0].set_xlabel('Sentiment')
        axes[0, 0].set_ylabel('Count')

        # Pie chart
        axes[0, 1].pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=sns.color_palette('viridis', n_colors=len(sentiment_counts)))
        axes[0, 1].set_title('Sentiment Proportion')

        # Stacked Bar Chart
        sentiment_data = pd.DataFrame({'Sentiment': sentiment_counts.index, 'Count': sentiment_counts.values})
        sentiment_data['Percentage'] = (sentiment_data['Count'] / sentiment_data['Count'].sum()) * 100
        df_stacked = pd.DataFrame({
            'Sentiment': sentiment_data['Sentiment'],
            'Count': sentiment_data['Count'],
            'Percentage': sentiment_data['Percentage']
        })

        df_stacked.plot(kind='bar', x='Sentiment', stacked=True, color=sns.color_palette('viridis', n_colors=len(sentiment_counts)), ax=axes[1, 0])
        axes[1, 0].set_title('Sentiment Stacked Bar Chart')
        axes[1, 0].set_xlabel('Sentiment')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].legend(['Count'])

        # Remove the unused subplot (axes[1, 1])
        fig.delaxes(axes[1, 1])

        # Adjust layout
        plt.tight_layout()

        # Save the plot to a BytesIO object
        buffer = io.BytesIO()
        canvas = FigureCanvas(fig)
        canvas.print_png(buffer)
        plt.close(fig)

        # Encode the plot as a base64 string
        plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return JsonResponse({'plot_data': plot_data})

    return render(request, 'ML/HomePageReview.html')