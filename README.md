# movie_project

In this project we scraped IMDB in search of the results that would support our hypothesis about movie reviews written by both IMDB users and critics. We asked ourselves, aside from the obvious factors, such as budget, famous actors, etc., what makes a person write a positive review?

It may not be obvious, but we assumed that the IMDB Parental Guide may somehow correlate with the reviews. The website categorizes different 'vices' of the movie, such as drug use, strong language, nudity, and rates them on a scale from 'none' to 'severe'. Looking at the data we tried to figure out if there is a correlation between critics' preferences and this scale. Comparing the data from ten years ago with modern day movies resulted in some very interesting findings.

Also we assumed that critics and users are somehow biased. There is a chance that if your friends or colleagues liked a certain movie, you will write a positive review as well. This analysis made us realize that there are at least four types of rating distributions.

We used matplotlib, seaborn, and plotly to illustrate our results.

Subset of data used: top 500 American Feature Films with the highest box-office 2017-19
