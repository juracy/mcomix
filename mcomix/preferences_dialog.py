"""preferences_dialog.py - Preferences dialog."""

import operator
import gtk
import gobject
import preferences_page
import image_tools
import constants
from preferences import prefs
from debug import log

_dialog = None

class _PreferencesDialog(gtk.Dialog):

    """The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user.
    """

    def __init__(self, window):
        gtk.Dialog.__init__(self, _('Preferences'), window, gtk.DIALOG_MODAL,
             (#gtk.STOCK_REFRESH, constants.RESPONSE_REVERT_TO_DEFAULT,
              gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self._window = window
        self.set_has_separator(False)
        self.set_resizable(True)
        self.set_default_response(gtk.RESPONSE_CLOSE)

        self.connect('response', self._response)

        notebook = gtk.Notebook()
        self.vbox.pack_start(notebook)
        self.set_border_width(4)
        notebook.set_border_width(6)

        appearance = self._init_appearance_tab()
        notebook.append_page(appearance, gtk.Label(_('Appearance')))
        behaviour = self._init_behaviour_tab()
        notebook.append_page(behaviour, gtk.Label(_('Behaviour')))
        display = self._init_display_tab()
        notebook.append_page(display, gtk.Label(_('Display')))
        advanced = self._init_advanced_tab()
        notebook.append_page(advanced, gtk.Label(_('Advanced')))

        self.show_all()

    def _init_appearance_tab(self):
        # ----------------------------------------------------------------
        # The "Appearance" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(80)
        page.new_section(_('Background'))

        fixed_bg_button = gtk.RadioButton(None, '%s:' %
            _('Use this colour as background'))
        fixed_bg_button.set_tooltip_text(
            _('Always use this selected colour as the background colour.'))
        fixed_bg_button.connect('toggled', self._check_button_cb, 'color box bg')
        bg_color_button = gtk.ColorButton(gtk.gdk.Color(*prefs['bg colour']))
        bg_color_button.connect('color_set', self._color_button_cb, 'bg colour')

        page.add_row(fixed_bg_button, bg_color_button)

        dynamic_bg_button = gtk.RadioButton(fixed_bg_button,
            _('Use dynamic background colour.'))
        dynamic_bg_button.set_active(prefs['smart bg'])
        dynamic_bg_button.connect('toggled', self._check_button_cb, 'smart bg')
        dynamic_bg_button.set_tooltip_text(
            _('Automatically pick a background colour that fits the viewed image.'))

        page.add_row(dynamic_bg_button)

        page.new_section(_('Thumbnails'))

        thumb_fixed_bg_button = gtk.RadioButton(None, '%s:' %
            _('Use this colour as the thumbnail background'))
        thumb_fixed_bg_button.set_tooltip_text(
            _('Always use this selected colour as the thumbnail background colour.'))
        thumb_fixed_bg_button.connect('toggled', self._check_button_cb, 'color box thumb bg')
        thumb_bg_color_button = gtk.ColorButton(gtk.gdk.Color(*prefs['thumb bg colour']))
        thumb_bg_color_button.connect('color_set', self._color_button_cb, 'thumb bg colour')

        page.add_row(thumb_fixed_bg_button, thumb_bg_color_button)

        thumb_dynamic_bg_button = gtk.RadioButton(thumb_fixed_bg_button,
            _('Use the dynamic background colour for the thumbnail background.'))
        thumb_dynamic_bg_button.set_active(prefs['smart thumb bg'])
        thumb_dynamic_bg_button.set_tooltip_text(
            _('Automatically use the colour that fits the viewed image for the thumbnail background.'))
        thumb_dynamic_bg_button.connect('toggled', self._check_button_cb, 'smart thumb bg')

        page.add_row(thumb_dynamic_bg_button)

        """
        same_as_main_bg_button = gtk.RadioButton(thumb_dynamic_bg_button,
            _('Use the same background colour as the main background.'))
        same_as_main_bg_button.connect('toggled', self._check_button_cb, 'thumbnail bg uses main colour')
        same_as_main_bg_button.set_tooltip_text(
            _('The thumbnail background will use the same colour as the main image background colour.'))

        page.add_row(same_as_main_bg_button)
        """

        label = gtk.Label('%s:' % _('Thumbnail size (in pixels)'))
        adjustment = gtk.Adjustment(prefs['thumbnail size'], 20, 500, 1, 10)
        thumb_size_spinner = gtk.SpinButton(adjustment)
        thumb_size_spinner.connect('value_changed', self._spinner_cb,
            'thumbnail size')
        page.add_row(label, thumb_size_spinner)

        thumb_number_button = gtk.CheckButton(
            _('Show page numbers on thumbnails.'))
        thumb_number_button.set_active(
            prefs['show page numbers on thumbnails'])
        thumb_number_button.connect('toggled', self._check_button_cb,
            'show page numbers on thumbnails')
        page.add_row(thumb_number_button)

        thumb_as_preview_icon = gtk.CheckButton(
            _('Use archive thumbnail as application icon.'))
        thumb_as_preview_icon.set_tooltip_text(
            _('By enabling this setting, the first page of a book will be used as application icon instead of the standard icon.'))
        thumb_as_preview_icon.set_active(
            prefs['archive thumbnail as icon'])
        thumb_as_preview_icon.connect('toggled', self._check_button_cb,
            'archive thumbnail as icon')
        page.add_row(thumb_as_preview_icon)

        page.new_section(_('Transparency'))
        checkered_bg_button = gtk.CheckButton(
            _('Use checkered background for transparent images.'))
        checkered_bg_button.set_active(
            prefs['checkered bg for transparent images'])
        checkered_bg_button.connect('toggled', self._check_button_cb,
            'checkered bg for transparent images')
        checkered_bg_button.set_tooltip_text(
            _('Use a grey checkered background for transparent images. If this preference is unset, the background is plain white instead.'))
        page.add_row(checkered_bg_button)

        return page

    def _init_behaviour_tab(self):
        # ----------------------------------------------------------------
        # The "Behaviour" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(80)
        page.new_section(_('Scroll'))
        smart_space_button = gtk.CheckButton(
            _('Use smart space key scrolling.'))
        smart_space_button.set_active(prefs['smart space scroll'])
        smart_space_button.connect('toggled', self._check_button_cb,
            'smart space scroll')
        smart_space_button.set_tooltip_text(
            _('Use smart scrolling with the space key. Normally the space key scrolls only right down (or up when shift is pressed), but with this preference set it also scrolls sideways and so tries to follow the natural reading order of the comic book.'))
        page.add_row(smart_space_button)

        flip_with_wheel_button = gtk.CheckButton(
            _('Flip pages when scrolling off the edges of the page.'))
        flip_with_wheel_button.set_active(prefs['flip with wheel'])
        flip_with_wheel_button.connect('toggled', self._check_button_cb,
            'flip with wheel')
        flip_with_wheel_button.set_tooltip_text(
            _('Flip pages when scrolling "off the page" with the scroll wheel or with the arrow keys. It takes n consecutive "steps" with the scroll wheel or the arrow keys for the pages to be flipped.'))
        page.add_row(flip_with_wheel_button)

        auto_open_next_button = gtk.CheckButton(
            _('Automatically open the next archive.'))
        auto_open_next_button.set_active(prefs['auto open next archive'])
        auto_open_next_button.connect('toggled', self._check_button_cb,
            'auto open next archive')
        auto_open_next_button.set_tooltip_text(
            _('Automatically open the next archive in the directory when flipping past the last page, or the previous archive when flipping past the first page.'))
        page.add_row(auto_open_next_button)

        label = gtk.Label('%s:' % _('Number of pixels to scroll per arrow key press'))
        adjustment = gtk.Adjustment(prefs['number of pixels to scroll per key event'], 1, 500, 1, 3)
        scroll_key_spinner = gtk.SpinButton(adjustment, digits=0)
        scroll_key_spinner.connect('value_changed', self._spinner_cb,
            'number of pixels to scroll per key event')
        scroll_key_spinner.set_tooltip_text(
            _('Set the number of pixels to scroll on a page when using the arrow keys.'))
        page.add_row(label, scroll_key_spinner)

        label = gtk.Label('%s:' % _('Number of pixels to scroll per mouse wheel turn'))
        adjustment = gtk.Adjustment(prefs['number of pixels to scroll per mouse wheel event'], 1, 500, 1, 3)
        scroll_key_spinner = gtk.SpinButton(adjustment, digits=0)
        scroll_key_spinner.connect('value_changed', self._spinner_cb,
            'number of pixels to scroll per mouse wheel event')
        scroll_key_spinner.set_tooltip_text(
            _('Set the number of pixels to scroll on a page when using a mouse wheel.'))
        page.add_row(label, scroll_key_spinner)

        label = gtk.Label('%s:' % _('Number of "steps" to take before flipping the page'))
        adjustment = gtk.Adjustment(prefs['number of key presses before page turn'], 1, 100, 1, 3)
        flipping_spinner = gtk.SpinButton(adjustment, digits=0)
        flipping_spinner.connect('value_changed', self._spinner_cb,
            'number of key presses before page turn')
        flipping_spinner.set_tooltip_text(
            _('Set the number of "steps" needed to flip to the next or previous page.  Less steps will allow for very fast page turning but you might find yourself accidentally turning pages.'))
        page.add_row(label, flipping_spinner)

        page.new_section(_('Double page mode'))

        step_length_button = gtk.CheckButton(
            _('Flip two pages in double page mode.'))
        step_length_button.set_active(prefs['double step in double page mode'])
        step_length_button.connect('toggled', self._check_button_cb,
            'double step in double page mode')
        step_length_button.set_tooltip_text(
            _('Flip two pages, instead of one, each time we flip pages in double page mode.'))
        page.add_row(step_length_button)

        virtual_double_button = gtk.CheckButton(
            _('Show only one wide image in double page mode.'))
        virtual_double_button.set_active(
            prefs['no double page for wide images'])
        virtual_double_button.connect('toggled', self._check_button_cb,
            'no double page for wide images')
        virtual_double_button.set_tooltip_text(
            _("Display only one image in double page mode, if the image's width exceeds its height. The result of this is that scans that span two pages are displayed properly (i.e. alone) also in double page mode."))
        page.add_row(virtual_double_button)

        page.new_section(_('Files'))

        auto_open_last_button = gtk.CheckButton(
            _('Automatically open the last viewed file on startup.'))
        auto_open_last_button.set_active(prefs['auto load last file'])
        auto_open_last_button.connect('toggled', self._check_button_cb,
            'auto load last file')
        auto_open_last_button.set_tooltip_text(
            _('Automatically open, on startup, the file that was open when MComix was last closed.'))
        page.add_row(auto_open_last_button)

        store_recent_button = gtk.CheckButton(
            _('Store information about recently opened files.'))
        store_recent_button.set_active(prefs['store recent file info'])
        store_recent_button.connect('toggled', self._check_button_cb,
            'store recent file info')
        store_recent_button.set_tooltip_text(
            _('Add information about all files opened from within MComix to the shared recent files list.'))
        page.add_row(store_recent_button)

        return page

    def _init_display_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)
        page.new_section(_('Default modes'))
        double_page_button = gtk.CheckButton(
            _('Use double page mode by default.'))
        double_page_button.set_active(prefs['default double page'])
        double_page_button.connect('toggled', self._check_button_cb,
            'default double page')
        page.add_row(double_page_button)

        fullscreen_button = gtk.CheckButton(_('Use fullscreen by default.'))
        fullscreen_button.set_active(prefs['default fullscreen'])
        fullscreen_button.connect('toggled', self._check_button_cb,
            'default fullscreen')
        page.add_row(fullscreen_button)

        manga_button = gtk.CheckButton(_('Use manga mode by default.'))
        manga_button.set_active(prefs['default manga mode'])
        manga_button.connect('toggled', self._check_button_cb,
            'default manga mode')
        page.add_row(manga_button)

        page.new_section(_('Fullscreen'))
        hide_in_fullscreen_button = gtk.CheckButton(
            _('Automatically hide all toolbars in fullscreen.'))
        hide_in_fullscreen_button.set_active(prefs['hide all in fullscreen'])
        hide_in_fullscreen_button.connect('toggled', self._check_button_cb,
            'hide all in fullscreen')
        page.add_row(hide_in_fullscreen_button)

        page.new_section(_('Slideshow'))
        label = gtk.Label('%s:' % _('Slideshow delay (in seconds)'))
        adjustment = gtk.Adjustment(prefs['slideshow delay'] / 1000.0,
            0.5, 3600.0, 0.1, 1)
        delay_spinner = gtk.SpinButton(adjustment, digits=1)
        delay_spinner.set_size_request(80, -1)
        delay_spinner.connect('value_changed', self._spinner_cb,
            'slideshow delay')
        page.add_row(label, delay_spinner)

        label = gtk.Label('%s:' % _('Slideshow step (in pixels)'))
        adjustment = gtk.Adjustment(prefs['number of pixels to scroll per slideshow event'],
            -500, 500, 1, 1)
        slideshow_step_spinner = gtk.SpinButton(adjustment, digits=0)
        slideshow_step_spinner.set_size_request(80, -1)
        slideshow_step_spinner.connect('value_changed', self._spinner_cb,
            'number of pixels to scroll per slideshow event')
        slideshow_step_spinner.set_tooltip_text(
            _('Specify the number of pixels to scroll while in slideshow mode. A positive value will scroll forward, a negative value will scroll backwards, and a value of 0 will cause the slideshow to always flip to a new page.'))
        page.add_row(label, slideshow_step_spinner)

        slideshow_auto_open_button = gtk.CheckButton(
            _('During a slideshow automatically open the next archive.'))
        slideshow_auto_open_button.set_active(prefs['slideshow can go to next archive'])
        slideshow_auto_open_button.connect('toggled', self._check_button_cb,
            'slideshow can go to next archive')
        slideshow_auto_open_button.set_tooltip_text(
            _('While in slideshow mode allow the next archive to automatically be opened.'))
        page.add_row(slideshow_auto_open_button)

        page.new_section(_('Rotation'))
        auto_rotate_button = gtk.CheckButton(
            _('Automatically rotate images according to their metadata.'))
        auto_rotate_button.set_active(prefs['auto rotate from exif'])
        auto_rotate_button.connect('toggled', self._check_button_cb,
            'auto rotate from exif')
        auto_rotate_button.set_tooltip_text(
            _('Automatically rotate images when an orientation is specified in the image metadata, such as in an Exif tag.'))
        page.add_row(auto_rotate_button)

        return page

    def _init_advanced_tab(self):
        # ----------------------------------------------------------------
        # The "Advanced" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

        page.new_section(_('User interface language'))
        label = gtk.Label('%s:' % _('Language (needs restart)'))
        language_box = self._create_language_control()
        page.add_row(label, language_box)

        page.new_section(_('Cache'))

        create_thumbs_button = gtk.CheckButton(
            _('Store thumbnails for opened files.'))
        create_thumbs_button.set_active(prefs['create thumbnails'])
        create_thumbs_button.connect('toggled', self._check_button_cb,
            'create thumbnails')
        create_thumbs_button.set_tooltip_text(
            _('Store thumbnails for opened files according to the freedesktop.org specification. These thumbnails are shared by many other applications, such as most file managers.'))
        page.add_row(create_thumbs_button)

        delay_thumbs_button = gtk.CheckButton(
            _('Delay thumbnail generation.'))
        delay_thumbs_button.set_tooltip_text(
            _('Thumbnails are generated only when required, instead of directly after opening a new file.'))
        delay_thumbs_button.set_active(prefs['delay thumbnails'])
        delay_thumbs_button.connect('toggled', self._check_button_cb,
            'delay thumbnails')
        page.add_row(delay_thumbs_button)

        label = gtk.Label('%s:' % _('Maximum number of pages to store in the cache'))
        adjustment = gtk.Adjustment(prefs['max pages to cache'], -1, 500, 1, 3)
        cache_spinner = gtk.SpinButton(adjustment, digits=0)
        cache_spinner.connect('value-changed', self._spinner_cb,
                                            'max pages to cache')
        cache_spinner.set_tooltip_text(
            _('Set the max number of pages to cache. A value of -1 will cache the entire archive.'))
        page.add_row(label, cache_spinner)

        page.new_section(_('Magnifying Lens'))

        label = gtk.Label('%s:' % _('Magnifying lens size (in pixels)'))
        adjustment = gtk.Adjustment(prefs['lens size'], 50, 400, 1, 10)
        lens_size_spinner = gtk.SpinButton(adjustment)
        lens_size_spinner.connect('value_changed', self._spinner_cb,
            'lens size')
        lens_size_spinner.set_tooltip_text(
            _('Set the size of the magnifying lens. It is a square with a side of this many pixels.'))
        page.add_row(label, lens_size_spinner)
        label = gtk.Label('%s:' % _('Magnification factor'))
        adjustment = gtk.Adjustment(prefs['lens magnification'], 1.1, 10.0,
            0.1, 1.0)
        lens_magnification_spinner = gtk.SpinButton(adjustment, digits=1)
        lens_magnification_spinner.connect('value_changed', self._spinner_cb,
            'lens magnification')
        lens_magnification_spinner.set_tooltip_text(
            _('Set the magnification factor of the magnifying lens.'))
        page.add_row(label, lens_magnification_spinner)

        page.new_section(_('Comments'))
        label = gtk.Label('%s:' % _('Comment extensions'))
        extensions_entry = gtk.Entry()
        extensions_entry.set_size_request(200, -1)
        extensions_entry.set_text(', '.join(prefs['comment extensions']))
        extensions_entry.connect('activate', self._entry_cb)
        extensions_entry.connect('focus_out_event', self._entry_cb)
        extensions_entry.set_tooltip_text(
            _('Treat all files found within archives, that have one of these file endings, as comments.'))
        page.add_row(label, extensions_entry)

        page.new_section(_('Logging output'))
        label = gtk.Label('%s:' % _('Logging output'))
        loglevel_box = self._create_log_control()
        page.add_row(label, loglevel_box)

        return page

    def _response(self, dialog, response):
        if response == gtk.RESPONSE_CLOSE:
            _close_dialog()

        elif response == constants.RESPONSE_REVERT_TO_DEFAULT:
            # to be used to restore preferences to default
            pass

        else:
            # Other responses close the dialog, e.g. clicking the X icon on the dialog.
            _close_dialog()

    def _create_log_control(self):
        """ Creates and returns the combobox for log level selection. """
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        model.append((_('All debug messages'), log.DEBUG))
        model.append((_('Notices, warnings and errors'), log.INFO))
        model.append((_('Warnings and errors (Default)'), log.WARNING))
        model.append((_('Only errors'), log.ERROR))
        loglevel_box = gtk.ComboBox(model)

        # Determine current log level
        iter = model.get_iter_first()
        index = 0
        while iter:
            if model.get_value(iter, 1) == prefs['log level']:
                loglevel_box.set_active(index)
                break
            else:
                iter = model.iter_next(iter)
                index += 1

        cell = gtk.CellRendererText()
        loglevel_box.pack_start(cell, True)
        loglevel_box.add_attribute(cell, 'text', 0)
        loglevel_box.connect('changed', self._loglevel_changed_cb)

        return loglevel_box

    def _loglevel_changed_cb(self, combobox, *args):
        """ Callback for log level settings. """
        model_index = combobox.get_active()
        if model_index > -1:
            iter = combobox.get_model().iter_nth_child(None, model_index)
            text, level = combobox.get_model().get(iter, 0, 1)
            log.setLevel(level)
            prefs['log level'] = level

    def _create_language_control(self):
        """ Creates and returns the combobox for language selection. """
        languages = [
            (_('Auto-detect (Default)'), 'auto'),
            (_('Catalan'), 'ca'),
            (_('Czech'), 'cs'),
            (_('German'), 'de'),
            (_('Greek'), 'el'),
            (_('English'), 'en'),
            (_('Spanish'), 'es'),
            (_('Persian'), 'fa'),
            (_('French'), 'fr'),
            (_('Galician'), 'gl'),
            (_('Croatian'), 'hr'),
            (_('Hungarian'), 'hu'),
            (_('Indonesian'), 'id'),
            (_('Italian'), 'it'),
            (_('Japanese'), 'jp'),
            (_('Korean'), 'ko'),
            (_('Dutch'), 'nl'),
            (_('Polish'), 'pl'),
            (_('Portuguese'), 'pt_BR'),
            (_('Russian'), 'ru'),
            (_('Swedish'), 'sv'),
            (_('Ukrainian'), 'uk'),
            (_('Chinese (simplified)'), 'zh_CN'),
            (_('Chinese (traditional)'), 'zh_TW')]
        languages.sort(key=operator.itemgetter(0))

        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for name, lang_code in languages:
            model.append((name, lang_code))

        box = gtk.ComboBox(model)

        # Determine current log level
        iter = model.get_iter_first()
        index = 0
        while iter:
            if model.get_value(iter, 1) == prefs['language']:
                box.set_active(index)
                break
            else:
                iter = model.iter_next(iter)
                index += 1

        cell = gtk.CellRendererText()
        box.pack_start(cell, True)
        box.add_attribute(cell, 'text', 0)
        box.connect('changed', self._language_changed_cb)

        return box

    def _language_changed_cb(self, combobox, *args):
        """ Called whenever the language was changed. """
        model_index = combobox.get_active()
        if model_index > -1:
            iter = combobox.get_model().iter_nth_child(None, model_index)
            text, lang_code = combobox.get_model().get(iter, 0, 1)
            prefs['language'] = lang_code

    def _check_button_cb(self, button, preference):
        """Callback for all checkbutton-type preferences."""

        prefs[preference] = button.get_active()

        if preference == 'color box bg' and button.get_active():

            if not prefs['smart bg'] or not self._window.filehandler.file_loaded:
                self._window.set_bg_colour(prefs['bg colour'])

        elif preference == 'smart bg' and button.get_active():

            # if the color is no longer using the smart background then return it to the chosen color
            if not prefs[preference]:
                self._window.set_bg_colour(prefs['bg colour'])
            else:
                # draw_image() will set the main background to the smart background
                self._window.draw_image()

        elif preference == 'color box thumb bg' and button.get_active():

            if prefs[preference]:
                prefs['smart thumb bg'] = False
                prefs['thumbnail bg uses main colour'] = False

                self._window.thumbnailsidebar.change_thumbnail_background_color(prefs['thumb bg colour'])
            else:
                self._window.draw_image()

        elif preference == 'smart thumb bg' and button.get_active():

            if prefs[preference]:
                prefs['color box thumb bg'] = False
                prefs['thumbnail bg uses main colour'] = False

                pixbuf = self._window.left_image.get_pixbuf()
                if pixbuf:
                    bg_color = image_tools.get_most_common_edge_colour(pixbuf)
                    self._window.thumbnailsidebar.change_thumbnail_background_color(bg_color)
            else:
                self._window.draw_image()


        #elif preference == 'thumbnail bg uses main colour' and button.get_active():
            """
            if prefs[preference]:
                prefs['color box thumb bg'] = False
                prefs['smart thumb bg'] = False

                if prefs['smart bg']:

                    self._window.draw_image()
                else:
                    self._window.thumbnailsidebar.change_thumbnail_background_color(prefs['bg colour'])
            else:
                self._window.draw_image()
            """
        elif preference in ('checkered bg for transparent images',
          'no double page for wide images', 'auto rotate from exif'):
            self._window.draw_image()

        elif (preference == 'hide all in fullscreen' and
            self._window.is_fullscreen):
            self._window.draw_image()

        elif preference == 'show page numbers on thumbnails':
            self._window.thumbnailsidebar.toggle_page_numbers_visible()

    def _color_button_cb(self, colorbutton, preference):
        """Callback for the background colour selection button."""

        colour = colorbutton.get_color()

        if preference == 'bg colour':
            prefs['bg colour'] = colour.red, colour.green, colour.blue

            if not prefs['smart bg'] or not self._window.filehandler.file_loaded:
                self._window.set_bg_colour(prefs['bg colour'])

        elif preference == 'thumb bg colour':

            prefs['thumb bg colour'] = colour.red, colour.green, colour.blue

            if not prefs['smart thumb bg'] or not self._window.filehandler.file_loaded:
                self._window.thumbnailsidebar.change_thumbnail_background_color( prefs['thumb bg colour'] )

    def _spinner_cb(self, spinbutton, preference):
        """Callback for spinner-type preferences."""
        value = spinbutton.get_value()

        if preference == 'lens size':
            prefs[preference] = int(value)

        elif preference == 'lens magnification':
            prefs[preference] = value

        elif preference == 'slideshow delay':
            prefs[preference] = int(value * 1000)
            self._window.slideshow.update_delay()

        elif preference == 'number of pixels to scroll per slideshow event':
            prefs[preference] = int(value)

        elif preference == 'number of pixels to scroll per key event':
            prefs[preference] = int(value)

        elif preference == 'number of pixels to scroll per mouse wheel event':
            prefs[preference] = int(value)

        elif preference == 'thumbnail size':
            prefs[preference] = int(value)
            self._window.thumbnailsidebar.resize()
            self._window.draw_image()

        elif preference == 'max pages to cache':
            prefs[preference] = int(value)
            self._window.imagehandler.do_cacheing()

        elif preference == 'number of key presses before page turn':
            prefs['number of key presses before page turn'] = int(value)
            self._window._event_handler._extra_scroll_events = 0

    def _entry_cb(self, entry, event=None):
        """Callback for entry-type preferences."""
        text = entry.get_text()
        extensions = [e.strip() for e in text.split(',')]
        prefs['comment extensions'] = [e for e in extensions if e]
        self._window.filehandler.update_comment_extensions()

def open_dialog(action, window):
    """Create and display the preference dialog."""

    global _dialog

    # if the dialog window is not created then create the window
    if _dialog is None:
        _dialog = _PreferencesDialog(window)
    else:
        # if the dialog window already exists bring it to the forefront of the screen
        _dialog.present()

def _close_dialog():

    global _dialog

    # if the dialog window exists then destroy it
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None


# vim: expandtab:sw=4:ts=4
