# Wikipedia Import: Cold start (computing)

## Matched Term

Cold start (computing)

## Domain

behavioral_regularities

## Source

https://en.wikipedia.org/wiki/Cold_start_(computing)

## Description



## Summary

Cold start in computing refers to a problem where a system or its part was created or restarted and is not working at its normal operation. The problem can be related to initialising internal objects or populating cache or starting up subsystems.
In a typical web service system the problem occurs after restarting the server, and also when clearing the cache (e.g., after releasing new version). The first requests to the web service will cause significantly more load due to the server cache being populated, the browser cache being cleared, and new resources being requested. Other services like a caching proxy or web accelerator will also need time to gather new resources and operate normally.
Similar problem occurs when creating instances in a hosted environment and instances in cloud computing services.
Cold start (or cold boot) may also refer to a booting process of a single computer (or virtual machine). In this case services and other startup applications are executed after reboot. The system is typically made available to the user even though startup operations are still performed and slow down other operations.
Another type of problem is when the data model of a particular system requires connections between objects. In that case new objects will not operate normally until those connections are made. This is well known problem with recommender systems.
In some machine learning scenarios, with models where the training dataset is incrementally added to in time (e.g. in active learning), cold start refers to training the model on the so far obtained labeled pool with new data added de novo, instead of training the model on new data with all its knowledge from previous trainings (warm start). Unlike the previous mentioned instances, cold starting in these scenarios can yield better results of the model.

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.
