/*
 * This file is part of Workout Manager.
 * 
 * Workout Manager is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Workout Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 */

/*
 * This file provides integration to Ubuntu's Unity interface with WebApps.
 * 
 * For more details look at:
 * - http://developer.ubuntu.com/api/ubuntu-12.04/javascript/index.html
 * - http://developer.ubuntu.com/api/ubuntu-12.04/javascript/unity-web-api-reference.html
 * - http://developer.ubuntu.com/resources/app-developer-cookbook/unity/integrating-tumblr-to-your-desktop/
 */

// helper function, taken from https://bazaar.launchpad.net/~webapps/webapps-applications/trunk/view/head:/common/utils.js.in
function evalInPageContext(func) {
    var script = document.createElement('script');
    script.appendChild(document.createTextNode('(' + func + ')();'));
    (document.body || document.head || document.documentElement).appendChild(script);
}

// helper function, taken from https://bazaar.launchpad.net/~webapps/webapps-applications/trunk/view/head:/common/utils.js.in
function makeRedirector(link) {
    return function () {
        evalInPageContext('function() {window.location = "' + link + '";}');
    };
}

// Do the actual integration, not much to do though
function unityReady() {
    Unity.Launcher.removeActions();
    Unity.Launcher.addAction("Workouts", makeRedirector('http://wger.de/workout/overview'));
    Unity.Launcher.addAction("Weight chart", makeRedirector('http://wger.de/weight/overview/'));
    Unity.Launcher.addAction("Add weight entry", makeRedirector('http://wger.de/weight/add/'));
    Unity.Launcher.addAction("Nutrition plans", makeRedirector('http://wger.de/nutrition/overview/'));
}

// If we are using Ubuntu, call the Init method for Unity, otherwise, do nothing
try
{
    var Unity = external.getUnityObject(1);
    
    // Commented out till I make it work reliably
    /*
    Unity.init({name: "Workout Manager",
            iconUrl: "http://developer.ubuntu.com/wp-content/uploads/2012/08/icon1.png",
            onInit: unityReady,
            homepage: "http://gargancjan.lem:8000/"});
    */
} 
catch(err)
{
    
}
