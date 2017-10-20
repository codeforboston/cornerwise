define(["backbone", "model/parcel"],
       function(B, Parcel) {
           return B.Collection.extend({
               model: Parcel,

               url: "/parcel/list"
           });
       });
