% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/utilityFunctions.R
\name{getStationMetrics}
\alias{getStationMetrics}
\title{getStationMetrics}
\usage{
getStationMetrics(climateStations, sdate = "por", edate = "por",
  filePathAndRootname, metric = NULL)
}
\arguments{
\item{climateStations}{A list of one or more unique identifiers (uid) for climate stations. Can be a single item, a list of items, or a data frame of the findStation response.}

\item{sdate}{(optional) Default is period of record ("por"). If specific start date is desired, format as a string (yyyy-mm-dd or yyyymmdd). Note: must be included for departure metrics. The beginning of the desired date range.}

\item{edate}{(optional) Default is period of record ("por"). If specific end date is desired, format as a string (yyyy-mm-dd or yyyymmdd). The end of the desired date range.}

\item{filePathAndRootname}{File path and root name for output CSV files. Do not include extension.}

\item{metric}{(optional) Default is all station metrics for temperature and precipitation. If used, returns values for specified metric.}
}
\value{
CSV files by metric
}
\description{
Requests Environmental Setting protocol metrics for a set of stations
}
