var inputs = document.querySelectorAll('.autocomplete');
for(var i = 0; i < inputs.length; i++){
    var autocomplete = new google.maps.places.Autocomplete(inputs[i],{types: ['(cities)']});
    // google.maps.event.addListener(autocomplete, 'place_changed', function(){
    //     var place = autocomplete.getPlace();
    // })
};



function mindate(){
    var dtToday = new Date();
    
    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();
    
    var minDate = year + '-' + month + '-' + day;
    var start = document.querySelector("#startdate")
    start.min = minDate
    // $('#startdate').attr('min', minDate);
};

mindate();