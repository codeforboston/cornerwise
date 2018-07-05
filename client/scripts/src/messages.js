define([], function() {
    return {
        confirmNewSubscription: {
            title: "Confirm new subscription",
            text: "You already signed up to receive notifications. If you want to add this new address, please confirm by clicking the Confirm link in your email."
        },
        overwriteExistingSubscription: {
            title: "Overwrite existing subscription?",
            text: "Looks like you have a subscription already. We've emailed a link to {response.email} that will confirm the new subscription. If you do nothing, your old subscription will remain active."
        },
        subscriptionCreated: {
            title: "You're subscribed!",
            text: "You will now receive updates when the proposals are updated."
        },
        confirmSubscription: {
            title: "Please confirm your email",
            text: "Thanks for registering! We've sent a message to {response.email} containing a link to confirm your email address. Once you confirm, then we can start sending you updates."
        },
        confirmSubscriptionRepeat: {
            title: "Please confirm your email",
            text: "Looks like you've tried to register more than once! We've sent you another email. Please use the link there to confirm your account."
        },

        subscribeInstructions: "Double-click the map or enter an address in the search box above to set the area you want to receive updates about. We will send updates about projects in the circle to the email address you provide.",

        addressNotFound: {
            text: "I couldn't find that address.",
            className: "error"
        }
    };
});
