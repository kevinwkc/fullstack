


You will develop a single page application featuring a map of your neighborhood or a neighborhood you would like to visit

API
============
google map api + 3rd party api with documentation
google street/place: map API should be called only once.
https://developers-google-com.ezproxy.torontopubliclibrary.ca/places/supported_types
https://developers.google.com/maps/documentation/streetview/intro

key='AIzaSyC3nmRdB-mgw_Z-SUUMSvVVxOtK_FwuQZY'
<script src="http://maps.googleapis.com/maps/api/js?libraries=places&key=[YOUR_API_KEY]"></script>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"
  type="text/javascript"></script>
wiki
ny time
http://developer.nytimes.com/
Geographic API: 1d8e341aba9345a08f39099067f77582

instagram
ab24a1e6bee946b792ce3315ec373e8c
  
http://api.openweathermap.org/data/2.5/forecast/daily?lat=43&lon=-79&cnt=10&mode=json&appid=54e6988e2dde530247b6bb6a31a8c2ef

{"city":{"id":1851632,"name":"Shuzenji","coord":{"lon":138.933334,"lat":34.966671},"country":"JP","population":0},"cod":"200","message":0.4031,"cnt":10,

"list":[{"dt":1476064800,"temp":{"day":292.33,"min":292.33,"max":293.12,"night":293.11,"eve":293.08,"morn":292.97},"pressure":1020.33,"humidity":100,"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"speed":10.26,"deg":38,"clouds":92},{"dt":1476151200,"temp":{"day":293.2,"min":292.61,"max":293.8,"night":293.61,"eve":293.65,"morn":292.61},"pressure":1022.11,"humidity":100,"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02d"}],"speed":8.21,"deg":37,"clouds":8},{"dt":1476237600,"temp":{"day":293.73,"min":292.74,"max":295.12,"night":293.84,"eve":294.81,"morn":292.74},"pressure":1018.54,"humidity":100,"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"speed":5.27,"deg":39,"clouds":88},{"dt":1476324000,"temp":{"day":291.74,"min":290.42,"max":293.21,"night":290.54,"eve":293.21,"morn":290.42},"pressure":1004.07,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":5.1,"deg":48,"clouds":24,"rain":1.37},{"dt":1476410400,"temp":{"day":291.63,"min":289.97,"max":294.78,"night":291.14,"eve":294.78,"morn":289.97},"pressure":1003.19,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":3.41,"deg":19,"clouds":75,"rain":2.02},{"dt":1476496800,"temp":{"day":289.74,"min":289.12,"max":292.89,"night":289.12,"eve":292.89,"morn":289.41},"pressure":1008.19,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":4.11,"deg":38,"clouds":16,"rain":1.04},{"dt":1476583200,"temp":{"day":291.28,"min":287.77,"max":293.19,"night":291.38,"eve":293.19,"morn":287.77},"pressure":1008.95,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":4.24,"deg":42,"clouds":83,"rain":1.06},{"dt":1476669600,"temp":{"day":291.34,"min":291.22,"max":292.43,"night":292.31,"eve":292.43,"morn":291.22},"pressure":992.37,"humidity":0,"weather":[{"id":502,"main":"Rain","description":"heavy intensity rain","icon":"10d"}],"speed":6.72,"deg":36,"clouds":100,"rain":41.03},{"dt":1476756000,"temp":{"day":293.12,"min":291.86,"max":295.61,"night":292.23,"eve":295.61,"morn":291.86},"pressure":985.25,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":1.33,"deg":63,"clouds":78,"rain":3.47},{"dt":1476842400,"temp":{"day":290.31,"min":289.44,"max":290.76,"night":289.44,"eve":290.59,"morn":290.76},"pressure":1001.69,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":4.8,"deg":61,"clouds":73,"rain":10.92}]}  
  


JAVASCRIPT design patterns 
=============================
https://www.udacity.com/course/javascript-design-patterns--ud989-nd
Things that should not be handled by Knockout: anything the Maps API is used for, creating markers, tracking click events on markers, making the map, refreshing the map. 

http://knockoutjs.com/
Knockout must be used to handle the list, filter, and any other information on the page that is subject to changing state. 
**Tracking click events on list items should be handled with Knockout.
**Creating your markers as a part of your ViewModel is allowed (and recommended). Creating them as Knockout observables is not.

AJAX error handling
===========================
http://ericduran.github.io/chromeHAR/
https://www.udacity.com/course/intro-to-ajax--ud110-nd
A message is displayed notifying the user that the data can't be loaded, OR There are no negative repercussions to the UI. 

mock error: http://www.digitaltrends.com/computing/how-to-block-a-website/

http://api.jquery.com/jquery.ajax/#jqXHR

project
==================
mobile first, map with marker, list view, search bar to filter list/marker
marker clickable[popup info], change style when click on
update list as well as marker
search filter trigger update list and marker


https://review.udacity.com/?_ga=1.28879934.309062196.1475106786#!/rubrics/17/view

https://classroom.udacity.com/nanodegrees/nd004/parts/00413454011/modules/271165859175462/lessons/2711658591239847/concepts/26294486380923#
Write code required to display map markers identifying at least 5 locations that you are interested in within this neighborhood. Your app should display those locations by default when the page is loaded.

list view of the set of locations
 
filter option that uses an input field to filter both the list view and the map markers displayed by default on load. The list view and the markers should update accordingly in real time. Providing a search function through a third-party API is not enough to meet specifications. This filter can be a text input or a dropdown menu.

Add functionality using third-party APIs to provide information when a map marker or list view entry is clicked (ex: Yelp reviews, Wikipedia, Flickr images, etc). Note that StreetView and Places don't count as an additional 3rd party API because they are libraries included in the Google Maps API.
Add functionality to open an infoWindow with the information above

Add functionality to animate a map marker when either the list item associated with it or the map marker itself is selected.

