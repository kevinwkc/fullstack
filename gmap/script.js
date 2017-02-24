var map;
var service;
var infowin;
function initMap() {
    var myloc = new google.maps.LatLng(43.847261, -79.370748);
    map = new google.maps.Map(document.getElementById('map'), {
        center: myloc,
        zoom: 13
    });

    var request = {
        location: myloc,
        radius: '5000',
        types: ['restaurant', 'bar', 'cafe']
    };

    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch(request, callback);
    
    infowin= new google.maps.InfoWindow({});
}

function callback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
        myVM.place(results);
    }else {
        console.log("placeservice status:" + status)
    }
}

function googleError(){
    $('#map').html("<h1>Google Map cannot get data</h1>")
}

var ViewModel = function() {
    var self = this;
    self.apiThreshold = 0// 10 * 68 * 1000; //time we should wait for next api call
    self.ajaxTime = Date.now() - self.apiThreshold; //init. ajaxTime call time
    self.ajaxResult = ko.observableArray(); //save all the ajax result
    self.contentString = ko.observable();
    self.query = ko.observable('');
    self.marker = ko.observableArray();
    self.place = ko.observableArray(); //init place
    self.subplace = ko.computed(function() { //store the temporary subset of places
        if (self.query() === '')
            return self.place();
        var query = self.query().toLowerCase();
        return ko.utils.arrayFilter(self.place(), function(p) {
            return p.name.toLowerCase().indexOf(query) !== -1;
        });
    }).extend({
        rateLimit: {
            timeout: 50, //prevent it to update too frequent
            method: 'notifyWhenChangesStop'
        }
    });

    self.filter = function() { //store the temporary subset of places
        if (self.query() === '')
            return self.place();
        var query = self.query().toLowerCase();
        return ko.utils.arrayFilter(self.place(), function(p) {
            return p.name.toLowerCase().indexOf(query) !== -1;
        });
    };

    //anime when clicked
    self.heroMarker = function(p) {

        ko.utils.arrayForEach(self.marker(), function(m) {

            if (m.id === p.id) { 
                google.maps.event.trigger(m, 'click');
            }
        });
    };

    //check if we have persiste the ajax result already
    self.gotAjax = function(name) {
        console.log("ajax length" + self.ajaxResult().length);
        for (var i = 0; i < self.ajaxResult().length; i++) {
            if (self.ajaxResult()[i].id === name) {
                return self.ajaxResult()[i];
            }
        }
        return null;
    };

    self.getMarkerByTitle = function(name) {
        for (var i = 0; i < self.marker().length; i++) {
            if (self.marker()[i].id === name) {
                return self.marker()[i];
            }
        }
        return null;
    };

    //pull 5 days forecast from ajax result
    self.getForecast = function(data) {
        var contentString = "<h1>5 days weather forecast</h1>";
        $.each(data.list, function(ind, w) {
            //console.log(w);
            var iconURL = "http://openweathermap.org/img/w/" + w.weather[0].icon + ".png";
            contentString += "<img src='" + iconURL + "'/>";
        });
        //console.log(contentString);
        return contentString;
    };

    //add marker
    self.addMarker = function(value) {
        //console.log(value.geometry.location);

        var m = new google.maps.Marker({
            map: map,
            title: value.name,
            id: value.id,
            position: value.geometry.location,
            lat: value.geometry.location.lat,
            lon: value.geometry.location.lng,
            animation: google.maps.Animation.DROP,
            icon: {
                url: value.icon,
                scaledSize: new google.maps.Size(30, 30)
            },
        });

        //add listener for marker
        m.addListener('click', function() {
            if (m.getAnimation() !== null) {
                m.setAnimation(null);
            } else {
                m.setAnimation(google.maps.Animation.BOUNCE);
                setTimeout(function(){m.setAnimation(null)}, 700);
            }
            
            var contentString = value.vicinity + "@" + value.geometry.location;

            //check whether we have persist the ajax result previously
            var gotit = self.gotAjax(m.id);

            //if not in persistent storage - ajaxResult, call ajax
            if ((Date.now() - self.ajaxTime) > self.apiThreshold && gotit === null) { // && self.ajaxResult.indexOf(m.title) == -1) {
                var url = "http://api.openweathermap.org/data/2.5/forecast/daily?lat=" + m.lat() + "&lon=" + m.lon() + "&cnt=5&mode=json&appid=54e6988e2dde530247b6bb6a31a8c2ef&units=metric";
                
                //async call
                $.getJSON(url).done( function(data, textStatus, jqXHR)  {
                    data = ko.toJS(data);
                    data.id = m.id;
                    //self.contentString(self.contentString()+self.getForecast(data));
                    console.log("json content:" + data.id);
                    self.ajaxResult.push(data);
                }).fail(function() {
                    //infowin.close()
                    contentString += "<h5>Cannot get data from API.</h5>";
                    infowin.setContent(contentString);
                    
                    infowin.open(map, m);
                });
                /*/MOCK DATA
                 
                      self.apiThreshold=5000;
                      setTimeout(function(){
                      data=ko.toJS(
                        {"city":{"id":1851632,"name":"Shuzenji","coord":{"lon":138.933334,"lat":34.966671},"country":"JP","population":0},"cod":"200","message":0.4031,"cnt":10,"list":[{"dt":1476064800,"temp":{"day":292.33,"min":292.33,"max":293.12,"night":293.11,"eve":293.08,"morn":292.97},"pressure":1020.33,"humidity":100,"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"speed":10.26,"deg":38,"clouds":92},{"dt":1476151200,"temp":{"day":293.2,"min":292.61,"max":293.8,"night":293.61,"eve":293.65,"morn":292.61},"pressure":1022.11,"humidity":100,"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02d"}],"speed":8.21,"deg":37,"clouds":8},{"dt":1476237600,"temp":{"day":293.73,"min":292.74,"max":295.12,"night":293.84,"eve":294.81,"morn":292.74},"pressure":1018.54,"humidity":100,"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"speed":5.27,"deg":39,"clouds":88},{"dt":1476324000,"temp":{"day":291.74,"min":290.42,"max":293.21,"night":290.54,"eve":293.21,"morn":290.42},"pressure":1004.07,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":5.1,"deg":48,"clouds":24,"rain":1.37},{"dt":1476410400,"temp":{"day":291.63,"min":289.97,"max":294.78,"night":291.14,"eve":294.78,"morn":289.97},"pressure":1003.19,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":3.41,"deg":19,"clouds":75,"rain":2.02},{"dt":1476496800,"temp":{"day":289.74,"min":289.12,"max":292.89,"night":289.12,"eve":292.89,"morn":289.41},"pressure":1008.19,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":4.11,"deg":38,"clouds":16,"rain":1.04},{"dt":1476583200,"temp":{"day":291.28,"min":287.77,"max":293.19,"night":291.38,"eve":293.19,"morn":287.77},"pressure":1008.95,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":4.24,"deg":42,"clouds":83,"rain":1.06},{"dt":1476669600,"temp":{"day":291.34,"min":291.22,"max":292.43,"night":292.31,"eve":292.43,"morn":291.22},"pressure":992.37,"humidity":0,"weather":[{"id":502,"main":"Rain","description":"heavy intensity rain","icon":"10d"}],"speed":6.72,"deg":36,"clouds":100,"rain":41.03},{"dt":1476756000,"temp":{"day":293.12,"min":291.86,"max":295.61,"night":292.23,"eve":295.61,"morn":291.86},"pressure":985.25,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":1.33,"deg":63,"clouds":78,"rain":3.47},{"dt":1476842400,"temp":{"day":290.31,"min":289.44,"max":290.76,"night":289.44,"eve":290.59,"morn":290.76},"pressure":1001.69,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":4.8,"deg":61,"clouds":73,"rain":10.92}]});
                          data.id=m.id;

                      contentString+=self.getForecast(data);
                      self.ajaxResult.push(data);
                      }, 1000);
                      */
                self.ajaxTime = Date.now();
            } else if (gotit !== null) {
                //infowin.close()
                contentString += self.getForecast(gotit);
                infowin.setContent(contentString);
                
                infowin.open(map, m);

            } else {
                //infowin.close()
                contentString += '<h5>Please wait 10 min for next api call</h5>';
                infowin.setContent(contentString);
                
                infowin.open(map, m);
            }

        });

        self.marker.push(m);
    }; //end add marker


    self.ajaxResult.subscribe(function(delta) {
        var status = delta[0];
        r = status.value;
        console.log("ajaxResult changed!");

        var m = self.getMarkerByTitle(r.id);
        //check from ajax result, and parse it
        console.log(m);
        //infowin.close()
        var contentString = '';
        contentString += self.getForecast(r);
        infowin.setContent(contentString);
        //infowin.push(infowindow);
        infowin.open(map, m);
    }, null, "arrayChange");

    //sync marker and place
    self.place.subscribe(function(newPlace) {
        self.clearMarker();
        $.each(newPlace, function(index, value) {
            self.addMarker(value);
        });
    });

    self.clearMarker = function() {
        ko.utils.arrayForEach(self.marker(), function(m) {
            m.setMap(null);
            m = null;
        });
        self.marker = ko.observableArray();
    };

    //sync the filter list with marker
    self.subplace.subscribe(function(newPlace) {
        self.clearMarker();

        $.each(newPlace, function(index, value) {
            self.addMarker(value);
        });
    });



};



var myVM = new ViewModel();

$(document).ready(function() {
    ko.applyBindings(myVM);

});