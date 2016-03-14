# -*- coding: utf-8 -*-
#
# tw2.ckeditor.widgets
#
# Copyright © 2016 Nils Philippsen <nils@tiptoe.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from tw2.core import Widget, Param, js_function
from tw2.forms import TextField, TextArea

from .resources import ckeditor_resources

__all__ = ('CKEditorTextField', 'CKEditorTextArea')


ckeditor_replace = js_function('CKEDITOR.replace')
ckeditor_inline = js_function('CKEDITOR.inline')


class CKEditorWidgetMixin(Widget):
    
    resources = ckeditor_resources

    _editor_config = Param(
        "low level configuration for CKEditor", default=None)

    inline = Param("whether to render an inline editor", default=False)


    def prepare(self):
        super(CKEditorWidgetMixin, self).prepare()

        cfg = self._editor_config if self._editor_config else {}

        if self.inline:
            call = ckeditor_inline(self.compound_id, cfg)
        else:
            call = ckeditor_replace(self.compound_id, cfg)
        self.add_call(call)


class CKEditorTextField(CKEditorWidgetMixin, TextField):

    pass


class CKEditorTextArea(CKEditorWidgetMixin, TextArea):

    pass
