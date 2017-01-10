# DATEXLA

The goal of this paper is to build a low-cost, easy-to-use, fully functional small-scale cloud computing experimental data center based on Raspberry pie, to design and implement a reasonable architecture, and to monitor system resources and visualize system logs. The work can be scaled to achieve a large-scale, low-power, efficient data center, Datexla(Low Cost **Da**ta Cen**te**r E**x**perimental P**la**tform).

![Cluster](https://github.com/Wsine/DATEXLA/blob/master/pic/Cluster.jpg?raw=true)

## Preparation

Please refer to [DATEXLA wiki](https://github.com/Wsine/DATEXLA/wiki)

## Directory Description

- app - application running in docker container
- config - one-touch configuration for cluster
- monitor - monitor cluster status and offer interface api
- visualization - transfer log file to UI
- reference - reading papers

## Associated project

[docker](https://github.com/datexla/docker), A forked project from [docker](https://github.com/docker/docker), datexla improves its remote api and schedule strategy

- Remote API
    - Multiple Containers Stats
    - Service Stats
    - Host Stats
- Schedule Strategy
    - Schedule base on resource

[go-cmdlog](https://github.com/datexla/go-cmdlog), A simple and crude go package for datexla logger

## Acknowledgements

- [docker](https://github.com/docker/docker), the open-source application container engine
- [swarmkit](https://github.com/docker/swarmkit), a toolkit for orchestrating distributed systems
- [Hypriot](http://blog.hypriot.com/), roaming the seven seas in search for golden container plunder
