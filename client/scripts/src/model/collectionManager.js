define(["backbone", "underscore", "appState"],
       function(B, _, appState) {
           /**
            * 
            */
           var CollectionManager = B.Collection.extend({
               /**
                * @param {Object} options
                * @param {Object} options.collections 
                */
               initialize: function(options) {
                   this.collections = options.collections;
                   this.activeCollection =
                       options.activeCollection ||
                       appState.getKey("c") ||
                       _.keys(options.collections)[0];

                   var self = this;

                   appState.onStateChange(function(newState, oldState) {
                       // Check if the active collection has changed:
                       if (newState.c !== oldState.c) {
                           self.setActiveCollection(newState.c);
                       }

                       // Check if the sort has changed:
                       if (newState.sort !== oldState.sort) {
                           var sort = newState.sort,
                               desc = sort[0] == "-",
                               sortKey = desc ? sort.slice(1) : sort;
                           self.getCollection().sortByField(sortKey, desc);
                       }
                   });
               },

               // Get the active collection:
               getCollection: function() {
                   return this.collections[this.activeCollection];
               },

               getCollectionName: function() {
                   return this.activeCollection;
               },

               setActiveCollection: function(name) {
                   if (name == this.activeCollection)
                       return;

                   var coll = this.collections[name],
                       old = this.getActiveCollection();

                   if (coll) {
                       this.activeCollection = name;
                       this.trigger("activeCollection", name, coll, old);
                       this.stopListening(old);
                       this.listenTo(coll, "all", this.forwardCollectionEvents);
                   }
               },

               forwardCollectionEvents: function() {
                   this.trigger.apply(this, arguments);
               },

               isSelectionEmpty: function() {
                   return !this.getCollection().getSelectionIds().length;
               }
           });

           return CollectionManager;
       });
