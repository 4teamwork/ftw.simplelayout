

.. contents:: Table of Contents




Introduction
============


SimpleLayout provides an intuitive way of adding and arranging the different
elements of a page such as paragraphs, images, files and links using
drag-and-drop functionality.
These elements are implemented as addable and easily arrangeable "blocks".
Because of the restricted dimensions of text, images and other content elements,
the general result is content with a uniform look and feel throughout the site.


Compatibility
-------------

Plone 4.3.x

.. image:: https://jenkins.4teamwork.ch/job/ftw.simplelayout-master-test-plone-4.3.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.simplelayout-master-test-plone-4.3.x.cfg


Installation
============

- Add the package to your buildout configuration:

::

    [instance]
    eggs +=
        ...
        ftw.simplelayout


Then you got several profile from wich you can choose from:

- ``ftw.simplelayout`` default profile - Installs everything you need include default
  DX based content to start with.

- ``ftw.simplelayout`` js lib profile - Only installs the JS library and the control panel.
  No example content, no further views. This profile is for Developers, who want to write their
  own simplelayout content types and views.

This package uses the `Simplelayout Javascript Lib <https://github.com/4teamwork/simplelayout>`_, which provides the basic functionality.
Further this package provides a Plone integration of the Simplelayout Lib:

- Overlays for manipulate blocks, such as adding, deleting and modifying.
- Saving the current Simplelayout state.
- Loading the configuration of a simplelayout page.
- Reloading blocks with additional parameters, view, or data attributes.



Usage
=====

First steps
-----------

It's a good idea to install the default profile, which ships some basic contenttypes, such as ContentPage and TextBlock.

Simply add a new ContentPage instead of a Plone Document. A Toolbox appears on right bottom, which allows you to create content on/in your ContentPage with Simplelayout.

By default you can choose between a 1 column, 2 Column or 4 Column layout.
Simplelayout adds an empty 1 column layout for you by default, so you can directly start adding a Block.

Just drag the Block of your choice, for example a TextBlock, into the layout. Enter title, body text and/or an image. Then click save.

As you see, you never going to leave the ContentPage, all actions with Simplelayout are asynchronous.
This means adding, deleting and editing always opens an overlay, where you can make the modifications.





Contenttypes
------------

Simplelayout ships by default with two content types.
One folderish type, the `ContentPage` and one block type, the `TextBlock`.


**ContentPage**

The ContentPage is a simple folderish dexterity based contenttype, which
does nearly nothing, but has the ``@@simplelayout-view`` view configured by default.
It's possible to add a ContentPage within a ContentPage

**TextBlock**

The TextBlock provides the following fields:

- ``Title`` (Well, this will be the title of the block, rendered as **h2**).
- Show title? (Decide if the title will be displayed or not).
- Text
- Image

Title, or Text, or the image is needed to successfully add a new block

The ``TextBlock`` configuration allows you to use this block to show text
only or images only, or of course both. There's no need of a single block for
images and a single block for text.

.. figure:: ./docs/_static/add_textblock.png
   :align: center
   :alt: Add TextBlock

   Add TextBlock


Behaviors
---------

- The Teaser behavior is enabled by default on `TextBlock`. It allows you to add an
  internal or external link to the block.


Simplelayout your site
----------------------

**Yes it's simple:**

- Add layouts by Drag'n'Drop
- Add Blocks by Drag'n'Drop
- Upload images directly by Drag'n'Drop [Comming soon]
- Change representation of blocks directly on the Block itself
- Responsive by default
- Create multiple column pages with ease.


Development
===========

**Python:**

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buidlout.cfg``
4. Shell: ``python boostrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Create new Block
----------------

Make your content blockish, needs only two steps.


1. The only difference between a block and other DX content types is the ``SimplelayoutBlockBehavior``. You can simply add the Block behavior to your content by adding the following line to FTI:

.. code-block:: xml

    <property name="behaviors">
        <element value="ftw.simplelayout.interfaces.ISimplelayoutBlock" />
    </property>

2. In order you block knows how to represent himself on a simplelayout page you need to register a ``block_view`` for your Block.

Register view with zcml:

.. code-block:: xml

    <browser:page
        for="my.package.content.IMyBlock"
        name="block_view"
        permission="zope2.View"
        class=".myblock.MyBlockView"
        template="templates/myblockview.pt"
        />

Corresponding template:

.. code-block:: html

      <h2 tal:content="context/Title">Title of block</h2>

      <!-- Assume you got a text field on your content -->
      <div tal:replace="structure here/text/output | nothing" />


Well basically that's it :-) You just created a new block!!


Create custom actions for Blocks
--------------------------------


Global Simplelayout configuration
---------------------------------


Create new Block representations
--------------------------------



Links
=====

- Main github project repository: https://github.com/4teamwork/ftw.simplelayout
- Issue tracker: https://github.com/4teamwork/ftw.simplelayout/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.simplelayout
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.simplelayout


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.simplelayout`` is licensed under GNU General Public License, version 2.

.. image:: https://cruel-carlota.pagodabox.com/a2410563766c51d4390fb7738fe40999
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.simplelayout
