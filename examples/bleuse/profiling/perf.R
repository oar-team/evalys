#!/usr/bin/Rscript

# clean environment
rm(list=ls());

# load libraries
library(ggplot2)
library(dplyr)

# colorblind friendly colors
cbPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

# user friendly names + time ordering for commits
commits <- list(
  intset='40c67da4ccf8',  # reference implementation
  wrapped='cebbabb56326',  # wrapped new API
  procset='484e302528a6'  # pure new API
)

# load data from measures
measures.dir <- 'perftest/'
instances <- list.files(measures.dir, pattern='*.csv')
data <- NULL
for (inst in instances) {
  df_inst <- read.csv(file.path(measures.dir, inst), header=TRUE, sep=';')

  # keep track of the origin file
  origin <- unlist(strsplit(inst, '[.]'))[2]
  df_inst <- mutate(df_inst, origin = origin)

  # combine with existing measures
  data <- bind_rows(data, df_inst)
  }
rm(origin, inst, df_inst)  # do not keep temporary elements

# helper function to compute confidence interval bounds
ci_bound <- function(threshold) return(qnorm(1-(1-threshold)/2))
ci_thld <- 0.99

# analyze data
aggreg_data <- data %>%
  mutate(
    runtime=ifelse(is.na(nbiter), e, pytimeit / nbiter)
  ) %>%
#  filter(method %in% c("freeslots", "detailedutilisation")) %>%
#  filter(method != "load") %>%
  group_by(method, trace) %>%
  mutate(
    normalized = (runtime - mean(runtime[commit==commits$intset])) / mean(runtime[commit==commits$intset])
  ) %>%
  group_by(method, trace, commit) %>%
  summarise(
    middle = mean(normalized),
    # assume normal distribution (>= 30 measure points) for CI
    lower = middle - ci_bound(ci_thld) * sd(normalized) / sqrt(n()),
    upper = middle + ci_bound(ci_thld) * sd(normalized) / sqrt(n())
  )

aggreg <- aggreg_data %>%
  ggplot(aes(x=trace, color=commit)) +
  geom_point(position=position_dodge(width=0.2), aes(y=middle)) +
  geom_errorbar(position='dodge', aes(ymin=lower, ymax=upper), width=0.2) +
  facet_grid(. ~ method, scales="free") +
  scale_color_manual(labels=names(commits), breaks=commits, values=cbPalette) +
  ylab('normalized runtime')

print(aggreg)