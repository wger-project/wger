# Promt for generating trophy icons

(these are the promts used to generate the trophy icons. As with everything AI, this can change
at any time in the future, so it's best to also just update one of the ones we already have so that
the design remains somewhat consistent)

Available background shapes:

* Circle (for basic trophies)
* Squircle (for special trophies)
* Shield (for milestone trophies)
* Star (for other trophies)
* Diamond (for other trophies)


## Promt

You are an expert graphic designer specializing in creating trophy icons for fitness applications.
Your task is to design a set of visually appealing and easily recognizable trophy icons that
represent various fitness achievements.

The icons should be modern, minimalist, and easily recognizable, even at smaller sizes.

The icons should be consistent in style and color to create a cohesive set.

Base shape (container): We're using solid, geometric shapes as the background, but not a hexagon, as it's already used in the app.

Aesthetics: Flat design. No gradients, shadows, or textures. Clean edges, but friendly.

Iconography: The icons inside are simplified, bold, and use clear metaphors (chains, weights, watches, etc.).

Typography: Text within the icons should be avoided, numbers (e.g. "5000 kg") are ok though

Color palette: Background shape: A fresh blue #2A4C7D. Text: white.
Other colors can be used for the icons inside to make them stand out and visually appealing.

The following is a list of trophies we want:

Group "number of workouts":
name: "Beginner", description: "Complete your first workout", type: "count", shape: "circle"
name: "Consistent", description: "Complete 10 workouts", type: "count", shape: "circle"
name: "Dedicated", description: "Complete 50 workouts", type: "count", shape: "circle"
name: "Obsessed", description: "Complete 100 workouts", type: "count", shape: "Squircle"
name: "Legend", description: "Complete 200 workouts", type: "count", shape: "Squircle"
name: "Veteran", description: "Complete 500 workouts", type: "count", shape: "Shield"
name: "Legend", description: "Complete 1000 workouts", type: "count", shape: "Shield"

Group "workout streaks":
name: "Unstoppable", description: "Maintain a 30-day workout streak", type: "sequence", shape: "circle"

Group "others":
name: "Weekend Warrior", description: "Work out on Saturday and Sunday for 4 consecutive weekends", type: "sequence", shape: "circle"
name: "Early Bird", description: "Complete a workout before 6:00 AM", type: "time", shape: "Diamond"
name: "Night Owl", description: "Complete a workout after 9:00 PM", type: "time", shape: "Diamond"
name: "New Year, New Me", description: "Work out on January 1st", type: "date", shape: "Star"
name: "Phoenix", description: "Return to training after being inactive for 30 days", type: "other", shape: "Star"
name: "Personal Record", description: "Repeatable Personal Record (PR) trophy", type: "pr", shape: "circle"

Group "cumulative weight lifted":
name: "Elephant lifter", description: "Lift a cumulative total of 5.000 kg", type: "volume", shape: "circle"
name: "Bus lifter", description: "Lift a cumulative total of 20.000 kg", type: "volume", shape: "circle"
name: "Plane lifter", description: "Lift a cumulative total of 50.000 kg", type: "volume", shape: "Squircle"
name: "Blue whale lifter", description: "Lift a cumulative total of 150.000 kg", type: "volume", shape: "Squircle"
name: "Space Station lifter", description: "Lift a cumulative total of 450.000 kg", type: "volume", shape: "Shield"
name: "Millionaire", description: "Lift a cumulative total of 1.000.000 kg (that's a fully loaded space shuttle!)", type: "volume", shape: "Shield"
name: "Atlas", description: "Lift a cumulative total of 10.000.000 kg", type: "volume", shape: "Shield"
