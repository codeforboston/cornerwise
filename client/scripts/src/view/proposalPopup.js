define(["backbone", "jquery", "utils"],
       function(B, $, $u) {
           return B.View.extend({
               template: $u.templateWithUrl("/static/template/proposalPopup.html",
                                            {variable: "proposal"}),

               projectTemplate: $u.templateWithUrl("/static/template/projectProposalPopup.html",
                                                   {variable: "proposal"}),

               render: function() {
                   var promise = $.Deferred(),
                       self = this,
                       template = this.model.getProject() ? this.projectTemplate : this.template;

                   template(this.model,
                            function(html) {
                                self.$el.html(html);
                                promise.resolve();
                            });

                   return this;
               }
           });
       });
