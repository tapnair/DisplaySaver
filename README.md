# DisplaySaver
Fusion 360 Add-in for Saving Display conditions

![Display Saver Dialog](./resources/displaySaverUI.png)
## Usage:
First see [How to install sample Add-Ins and Scripts](https://rawgit.com/AutodeskFusion360/AutodeskFusion360.github.io/master/Installation.html)

This addin allows you to save and retrieve the display of components in the graphics window.

See a video here: https://youtu.be/pvL8eC3pYoY

If you select a saved display from the drop down it will revert the display to that condition.  New parts will retain their current state.  Selecting Current or cancel will revert to the hide/show state of all components when you entered the command.

If you select the check box you can create a new state based on the hide/show state of the components when you entered the command.

It stores the saved display information in a folder called displaySaver in your user directory.  

## Limitations
  * Since the display information is stored locally it will only be availabel on the computer it was created.  Looking to add some kind of cloud support in the future.
  * If you have two models of the same name they are not distinguished. POtentially will add project directory to file names.
  * Currently no way to delete saved displays

## License
Samples are licensed under the terms of the [MIT License](http://opensource.org/licenses/MIT). Please see the [LICENSE](LICENSE) file for full details.

## Written by

Created by Patrick Rainsberry <br /> (Autodesk Fusion 360 Business Development)
