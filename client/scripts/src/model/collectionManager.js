define(["backbone", "underscore", "appState"],
       function(B, _, appState) {
           /**
            * The collection manager keeps track of the active collection and
            * passes messages about the app state to that collection.
            */
           var CollectionManager = B.Collection.extend({
               /**
                * @param {Object} options
                * @param {Object} options.collections 
                */
               initialize: function(options) {
                   this.collections = options.collections;
                   var name =
                       options.activeCollection ||
                       appState.getKey("c") ||
                       _.keys(options.collections)[0];
                   this.setActiveCollection(name);

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

               getCollectionNames: function() {
                   return _.keys(this.collections);
               },

               setActiveCollection: function(name) {
                   if (name == this.activeCollection)
                       return;

                   var coll = this.collections[name],
                       old = this.collections[this.activeCollection];

                   if (coll) {
                       this.activeCollection = name;
                       this.trigger("activeCollection", name, coll, old);
                       this.stopListening(old);
                       this.listenTo(coll, "all",
                                     this._forwardCollectionEvents);
                   }
               },

               _forwardCollectionEvents: function(event) {
                   var args = _.drop(arguments, 1),
                       name = this.activeCollection;
                   this.trigger.apply(this, [event, name].concat(args));
               },

               isSelectionEmpty: function() {
                   return !this.getCollection().getSelectionIds().length;
               }
           });

           return CollectionManager;
       });
