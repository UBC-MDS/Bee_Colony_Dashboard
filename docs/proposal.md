Proposal
================

## Motivation and purpose

Our role: Data scientist consultancy firm

Target audience: Agricultural practitioners, Beekeepers/Apiarists

Bees are one of the most essential components of modern agriculture.
Most plants need to be pollinated by animal visitors, especially
insects. A wide variety of flowering plants, such as the everyday
visible fruits like apples and blueberries, require managed pollinators
to be able to ensure production. Honey bees are ideal for pollination
because they are easy to move and manage. However, during the winter of
2006-2007, some beekeepers in America began to report unusually high
losses of 30-90 percent of their hives. Colony loss has declined since
then but is still a concern. Since number of bee colonies is closely
related to agricultural production, there is a need for both
decision-makers and practitioners in the direction of agriculture to
know the status of local bee colonies, especially the number, loss
trend, and colony stressors.

To meet the needs of agricultural development, we decided to build a
data visualization app with open data to ensure that agricultural
practitioners can explore bee colony data visually. Our application will
display the number of bee colonies in each state of the United States
over the years and allow users to explore changes in colony numbers by
filtering by state and time.

## Description of the data

The honey bee colonies and stressors dataset was obtained from
[TidyTuesday](https://github.com/rfordatascience/tidytuesday/blob/master/data/2022/2022-01-11/readme.md)
who in turn obtained the raw data from the USDA.

The time series data are collected from a stratified sample of
operations that responded as having honey bees on the Bee and Honey
Inquiry and from the NASS list frame in USA. For operations with five or
more colonies, data was collected on a quarterly basis; operations with
less than five colonies were collected with an annual survey.

In our dashboard, we will visualize colony_n which is the number of
colonies in a state, through a time series plot and a geographic map.
Additionally, we visualize the percentage of colonies (stress_pct)
affected by different colony health stressors (stressor) for a state
over time through a series of stacked bar plots.

## Research questions and usage scenarios

Our project, the Bee Colony Dashboard helps identify the colony collapse
disorder over quarterly periods in the US. Some of key questions that
can be answered are:

1.  Which state has highest/lowest colony loss% over time?

2.  What causes colony collapse disorder?

3.  What specific problems(insights on stressors) certain state’s
    colonies face over time?

Below is a usage scenario of our dashboard:

Buzzing Bee is a beekeeping company interested in researching about the
colony loss across the US.Since the loss rates are high the beekeepers
are under pressure to create new colonies to offset losses each year.
The company wants to work with agriculture practitioners and farms to
keep the bee colonies stable without the need to add new colonies each
year.

John, is an apiarist working in Buzzing Bee and is assigned the project
to identify the states where colony loss% is very high and to study the
causes.

With the Bee Colony Dashboard, he will be able to identify bee colony
losses over quarterly periods in the US.The geographic map visual
illustrates how bee colony losses vary over each state for a single
period in time, and apiarists/beekeepers can gain an idea of the local
severity of colony stressors in different states. The time series plot
visualizes the number of colonies over time for a single state and will
inform apiarists/beekeepers of how problems affecting colonies
increase/decrease over time. The third visualization, the stacked bar
chart of stressors, gives insight on what specific problems a certain
state’s colonies face over time, and can provide crucial information on
what stressors need to be combated to improve colony health.
