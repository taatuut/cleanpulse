# cleanpulse
"Real-time insights for spotless performance". an application that focuses on reporting the cleaning activities of machines in a factory, including details such as the last cleaning time, duration, water usage, and energy usage. Relevant for CPG, like beer breweries and coffee-roasting factories.

## what we are aiming for
Real-time information into a high-tech industrial control room with multiple digital dashboards showing live data feeds. One dashboard highlights real-time cleaning activities of robotic and automated machines in a brewery and factory. Screens display animated timelines, sensor graphs, heatmaps of machine cleanliness, and event logs. Overlaid holographic UI elements show Solace PubSub+ messaging icons, AI analytics charts, and alerts. In the background, factory floors and brewing tanks are visible through glass walls, with autonomous cleaning robots in action. "Powered by CleanPulse AI".

## steps (concepot, please add/change)
- create application description and use ai event model wizard to create app with events
- follow outline at https://feeds.solace.dev/ to create feed (@magali, you had some ideas on topics and payload?)
- create feed(s) would be nice if these are semirandom so we cabn use ai to detect patterns in there, check if this is possible with feed
- create event mesh
- publish feed to mesh
- add ai agent as subscriber to detect patterns (like 'cleaning at night/weekend is cheaper because of energy cost', 'cleaning on friday uses way more chemicals because too long cleaning interval following Sun-Tue-Fri scheudle', just making these up) 
- publish or subscribe a analytics / dashboard

![hitech industrial control room with multiple digital dashboards showing live data feeds featuring real-time cleaning activities](https://github.com/user-attachments/assets/f9e7a312-6471-4631-a278-fd53e49e5218)
