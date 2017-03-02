$(function() {
    function RoomTempViewModel(parameters) {
        var self = this;

        self.roomTempModel = parameters[0];
        self.global_settings = parameters[1];
        self.roomTemp = ko.observable();
        self.isRaspi = ko.observable(false);

        self.onBeforeBinding = function () {
            self.settings = self.global_settings.settings.plugins.roomtemp;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "roomtemp") {
                return;
            }

            if (!data.hasOwnProperty("israspi")) {
                self.isRaspi(false);
                return;
            } else {
                self.isRaspi(true);
            }

            self.roomTemp(_.sprintf("Room: %.1f&deg;c", data.roomtemp));
        };
    }

    ADDITIONAL_VIEWMODELS.push([
        RoomTempViewModel, 
        ["temperatureViewModel", "settingsViewModel"],
        ["#navbar_plugin_roomtemp", "#settings_plugin_roomtemp"]
    ]);
});
