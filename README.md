# Supplementary materials for _Cognitive Rhythms: Unobtrusive and Continuous Sensing of Alertness Using a Mobile Phone_

[![DOI] (https://img.shields.io/badge/DOI-10.1145%2F2971648.2971712-blue.svg)](https://dx.doi.org/10.1145/2971648.2971712)

This repository contains supplementary materials for _Cognitive Rhythms: Unobtrusive and Continuous Sensing of Alertness Using a Mobile Phone_. UbiComp, 2016. DOI: [10.1145/2971648.2971712](https://dx.doi.org/10.1145/2971648.2971712)

## Assessing Alertness ##

To assess alertness, we used the Psychomotor Vigilance Test (PVT)
which is a _reaction time_ test. In this test, the user responds
to a visual stimulus shown at random intervals. Various statistical
summaries of response time have been shown to be indicative
of alertness.

In our paper, we operationalize alertness as relative response time(_RRT_).
The steps of computing RRT from PVT response time are as follows:

* The first step involves removing _false starts_ — cases where users
responded (wrongly) before the stimulus has been shown.
* Since a PVT session includes multiple visual stimuli tests,
we calculate the median response time (`MRT`<sub>s,p</sub>) for each
session `s` per person `p`.
* We then remove outlier sessions with `MRT`<sub>s,p</sub> falling outside
(mean ± 2.5 × SD) for each participant.
* Next, we take the mean `MRT`<sub>s,p</sub> across all of participant `p`’s
sessions to establish an individual baseline for participant `p`.
* Finally, we compute the RRT of a given session as its percentage deviation
from `p`’s individual baseline. That is, given a PVT session `s` for a participant
`p` with a median reaction time for that session of `MRT`<sub>s,p</sub>,
the corresponding RRT is calculated as:

<p align="center">
  ![RRT Equation](/images/eq-rrt.png?raw=true)
</p>

Here, MMRT<sub>p</sub> is the mean `MRT` averaged across all `N` sessions from
participant `p`:

<p align="center">
  ![MMRT equation](/images/eq-mmrt.png?raw=True)
</p>
