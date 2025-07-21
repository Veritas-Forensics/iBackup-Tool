import sys
import os
from datetime import datetime
from typing import Dict, Optional

try:
    from pymobiledevice3.exceptions import NoDeviceConnectedError, InvalidServiceError
    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.services.screenshot import ScreenshotService
    from pymobiledevice3.services.springboard import SpringBoardServicesService
    from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
    from pymobiledevice3.usbmux import select_device
    import tempfile
    import shutil
    from PIL import Image, ImageDraw, ImageFont
    import io
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install with: pip install pymobiledevice3 pillow")
    sys.exit(1)

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QPushButton, QLabel, QComboBox, QProgressBar, QPlainTextEdit,
        QMessageBox, QGroupBox, QFormLayout, QFileDialog, QLineEdit,
        QDialog, QTextEdit, QCheckBox, QScrollArea
    )
    from PyQt6.QtCore import QThread, pyqtSignal, Qt
    from PyQt6.QtGui import QPixmap, QIcon, QFont
except ImportError as e:
    print(f"Error importing PyQt6: {e}")
    print("Please install with: pip install PyQt6")
    sys.exit(1)

# --- License Agreement Dialog ---
class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Agreement - iDevice Manager")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.setup_ui()
        self.apply_stylesheet()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("End User License Agreement")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please read and accept the following terms before using iDevice Manager")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        # License text in scrollable area
        scroll_area = QScrollArea()
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText(self.get_license_text())
        scroll_area.setWidget(license_text)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Agreement checkbox
        self.agree_checkbox = QCheckBox("I have read and agree to the terms of this license agreement")
        self.agree_checkbox.stateChanged.connect(self.on_checkbox_changed)
        layout.addWidget(self.agree_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.decline_button = QPushButton("Decline")
        self.decline_button.clicked.connect(self.reject)
        
        self.accept_button = QPushButton("Accept & Continue")
        self.accept_button.setEnabled(False)
        self.accept_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.decline_button)
        button_layout.addStretch()
        button_layout.addWidget(self.accept_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def get_license_text(self):
        return """                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
state the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Also add information on how to contact you by electronic and paper mail.

  If the program does terminal interaction, make it output a short
notice like this when it starts in an interactive mode:

    <program>  Copyright (C) <year>  <name of author>
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, your program's commands
might be different; for a GUI interface, you would use an "about box".

  You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU GPL, see
<http://www.gnu.org/licenses/>.

  The GNU General Public License does not permit incorporating your program
into proprietary programs.  If your program is a subroutine library, you
may consider it more useful to permit linking proprietary applications with
the library.  If this is what you want to do, use the GNU Lesser General
Public License instead of this License.  But first, please read
<http://www.gnu.org/philosophy/why-not-lgpl.html>."""
        
    def on_checkbox_changed(self, state):
        self.accept_button.setEnabled(state == Qt.CheckState.Checked.value)
        
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QLabel {
                color: #ffffff;
            }
            
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                padding: 8px;
            }
            
            QCheckBox {
                color: #ffffff;
                font-weight: bold;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            
            QCheckBox::indicator:checked:after {
                content: "✓";
                color: white;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            
            QScrollArea {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
        """)

# --- Worker Thread for Backend Operations ---
class TaskWorker(QThread):
    log_updated = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    task_finished = pyqtSignal(str)
    
    device_info_ready = pyqtSignal(dict)

    def __init__(self, command, backup_directory=None):
        super().__init__()
        self.command = command
        self.backup_directory = backup_directory

    def run(self):
        self.log_updated.emit(f"Task '{self.command}' started...")
        self.progress_updated.emit(0)
        
        try:
            if self.command == 'backup':
                self.run_backup()
            elif self.command == 'device-info':
                self.run_get_device_info()
        except Exception as e:
            self.log_updated.emit(f"[ERROR] An unexpected error occurred: {e}")
            self.task_finished.emit("Task failed with an unexpected error.")
        finally:
            self.progress_updated.emit(0)

    def run_get_device_info(self):
        """Fetches device properties and a screenshot."""
        try:
            self.log_updated.emit("Searching for connected devices...")
            self.progress_updated.emit(10)
            
            # Select the first available device
            device = select_device()
            if not device:
                raise NoDeviceConnectedError("No USB devices found")
                
            self.log_updated.emit(f"Found device: {device}")
            self.progress_updated.emit(25)
            
            # Create lockdown client using the selected device
            self.log_updated.emit("Establishing lockdown connection...")
            lockdown = create_using_usbmux(device.serial)
            self.log_updated.emit("Device connected successfully")
            self.progress_updated.emit(50)
            
            # Get device information first
            self.log_updated.emit("Retrieving device information...")
            device_info = {
                'DeviceName': lockdown.get_value(domain=None, key='DeviceName') or 'Unknown Device',
                'ProductVersion': lockdown.get_value(domain=None, key='ProductVersion') or 'Unknown Version',
                'SerialNumber': lockdown.get_value(domain=None, key='SerialNumber') or 'Unknown Serial',
                'UniqueDeviceID': lockdown.get_value(domain=None, key='UniqueDeviceID') or 'Unknown UDID',
                'ProductType': lockdown.get_value(domain=None, key='ProductType') or 'Unknown Model',
                'BuildVersion': lockdown.get_value(domain=None, key='BuildVersion') or 'Unknown Build'
            }
            self.progress_updated.emit(60)
            
            # Try to get wallpaper screenshot first, then fallback to regular screenshot
            screenshot_captured = False
            
            # Check device pairing and SSL status first
            self.log_updated.emit("Checking device trust and pairing status...")
            try:
                # Test basic lockdown communication
                device_class = lockdown.get_value(domain=None, key='DeviceClass')
                ios_version = lockdown.get_value(domain=None, key='ProductVersion')
                self.log_updated.emit(f"Device class: {device_class}, iOS: {ios_version}")
                
                # Check if device requires trust dialog
                if not lockdown.get_value(domain=None, key='TrustedHostAttached'):
                    self.log_updated.emit("[WARNING] Device may not be trusted. Please check 'Trust This Computer' dialog on device.")
                
            except Exception as pairing_error:
                self.log_updated.emit(f"[WARNING] Pairing check failed: {pairing_error}")
            
            # Method 1: Try SpringBoard wallpaper screenshot with SSL error handling
            try:
                self.log_updated.emit("Attempting to capture wallpaper screenshot...")
                
                # Initialize SpringBoard service with error handling
                try:
                    springboard_service = SpringBoardServicesService(lockdown)
                    # Test service with simple call first
                    orientation = springboard_service.get_interface_orientation()
                    self.log_updated.emit(f"Device orientation: {orientation}")
                except Exception as ssl_error:
                    if "SSL" in str(ssl_error) or "BAD_LENGTH" in str(ssl_error):
                        self.log_updated.emit(f"[WARNING] SSL communication error: {ssl_error}")
                        self.log_updated.emit("This may be due to device trust issues or iOS version compatibility")
                        raise ssl_error
                    else:
                        raise ssl_error
                
                wallpaper_data = None
                
                # Try multiple wallpaper methods
                try:
                    # Method 1: Get home screen wallpaper PNG data
                    self.log_updated.emit("Trying home screen wallpaper...")
                    wallpaper_data = springboard_service.get_wallpaper_pngdata()
                    if wallpaper_data:
                        self.log_updated.emit("Got home screen wallpaper data")
                except Exception as e:
                    self.log_updated.emit(f"Home screen wallpaper failed: {e}")
                
                # Method 2: Try getting wallpaper preview images (if available)
                if not wallpaper_data:
                    try:
                        self.log_updated.emit("Trying wallpaper preview method...")
                        # Get available wallpapers first
                        wallpaper_names = ['Default', 'OriginalPhoto', 'UserPhoto']
                        for name in wallpaper_names:
                            try:
                                wallpaper_data = springboard_service.get_wallpaper_preview_image(name)
                                if wallpaper_data:
                                    self.log_updated.emit(f"Got wallpaper preview: {name}")
                                    break
                            except Exception:
                                continue
                    except Exception as e:
                        self.log_updated.emit(f"Wallpaper preview failed: {e}")
                
                # Method 3: Try getting app icon as alternative visual representation
                if not wallpaper_data:
                    try:
                        self.log_updated.emit("Trying to get app icons as alternative...")
                        
                        # Get icon state to find apps
                        icon_state = springboard_service.get_icon_state()
                        if icon_state and len(icon_state) > 0:
                            # Look for a common app like Settings, Phone, or Camera
                            common_apps = [
                                'com.apple.Preferences',  # Settings
                                'com.apple.camera',       # Camera
                                'com.apple.mobilephone',  # Phone
                                'com.apple.mobilesafari', # Safari
                                'com.apple.MobileSMS'     # Messages
                            ]
                            
                            for app_bundle in common_apps:
                                try:
                                    icon_data = springboard_service.get_icon_pngdata(app_bundle)
                                    if icon_data:
                                        wallpaper_data = icon_data
                                        self.log_updated.emit(f"Got app icon for display: {app_bundle}")
                                        break
                                except Exception:
                                    continue
                                    
                            # If no common apps found, try the first app from icon state
                            if not wallpaper_data and icon_state:
                                # Find first app with bundle ID from icon state
                                for page in icon_state:
                                    if isinstance(page, list):
                                        for item in page:
                                                if isinstance(item, dict) and 'bundleIdentifier' in item:
                                                    bundle_id = item['bundleIdentifier']
                                                    try:
                                                        icon_data = springboard_service.get_icon_pngdata(bundle_id)
                                                        if icon_data:
                                                            wallpaper_data = icon_data
                                                            self.log_updated.emit(f"Got icon from first app: {bundle_id}")
                                                            break
                                                    except Exception:
                                                        continue
                                                if wallpaper_data:
                                                    break
                                        if wallpaper_data:
                                            break
                        
                    except Exception as e:
                        self.log_updated.emit(f"App icon fallback failed: {e}")
                        
                
                if wallpaper_data:
                    # Add iPhone frame around the screenshot/wallpaper
                    try:
                        framed_data = self._create_device_frame(wallpaper_data)
                        device_info['screenshot'] = framed_data
                        self.log_updated.emit("Visual representation captured and framed successfully")
                    except Exception as frame_error:
                        self.log_updated.emit(f"Frame creation failed, using original: {frame_error}")
                        device_info['screenshot'] = wallpaper_data
                    screenshot_captured = True
                else:
                    raise Exception("No visual data could be retrieved")
                    
            except (InvalidServiceError, AttributeError, Exception) as wallpaper_error:
                self.log_updated.emit(f"[WARNING] Wallpaper screenshot not available: {wallpaper_error}")
                
                # If SSL error, provide user guidance
                if "SSL" in str(wallpaper_error) or "BAD_LENGTH" in str(wallpaper_error):
                    self.log_updated.emit("💡 Tip: SSL errors often indicate device trust issues")
                    self.log_updated.emit("💡 Try: 1) Check 'Trust This Computer' on device 2) Re-pair device 3) Update iOS")
            
            # Method 2: Fallback to regular screenshot if wallpaper failed
            if not screenshot_captured:
                try:
                    self.log_updated.emit("Attempting regular screenshot...")
                    screenshot_service = ScreenshotService(lockdown)
                    png_data = screenshot_service.take_screenshot()
                    
                    # Add iPhone frame around the screenshot
                    try:
                        framed_data = self._create_device_frame(png_data)
                        device_info['screenshot'] = framed_data
                        self.log_updated.emit("Regular screenshot captured and framed successfully")
                    except Exception as frame_error:
                        self.log_updated.emit(f"Frame creation failed, using original: {frame_error}")
                        device_info['screenshot'] = png_data
                        self.log_updated.emit("Regular screenshot captured successfully")
                    
                    screenshot_captured = True
                except (InvalidServiceError, Exception) as screenshot_error:
                    self.log_updated.emit(f"[WARNING] Regular screenshot not available: {screenshot_error}")
            
            # Method 3: Create a placeholder image when all screenshot methods fail
            if not screenshot_captured:
                try:
                    self.log_updated.emit("Creating placeholder device image...")
                    
                    # Create an iPhone-like device frame with placeholder
                    
                    # iPhone dimensions with frame
                    frame_width = 240
                    frame_height = 480
                    screen_width = 200
                    screen_height = 420
                    frame_thickness = 20
                    corner_radius = 25
                    
                    # Create image with device frame
                    img = Image.new('RGBA', (frame_width, frame_height), color=(0, 0, 0, 0))
                    draw = ImageDraw.Draw(img)
                    
                    # Draw iPhone frame (rounded rectangle)
                    frame_color = '#2c2c2c'
                    screen_color = '#000000'
                    
                    # Outer frame
                    draw.rounded_rectangle(
                        [0, 0, frame_width, frame_height], 
                        radius=corner_radius, 
                        fill=frame_color, 
                        outline='#404040', 
                        width=2
                    )
                    
                    # Screen area
                    screen_x = frame_thickness
                    screen_y = frame_thickness + 30  # Extra space for notch area
                    draw.rounded_rectangle(
                        [screen_x, screen_y, screen_x + screen_width, screen_y + screen_height], 
                        radius=15, 
                        fill=screen_color
                    )
                    
                    # iPhone notch (simplified)
                    notch_width = 60
                    notch_height = 8
                    notch_x = (frame_width - notch_width) // 2
                    notch_y = frame_thickness + 5
                    draw.rounded_rectangle(
                        [notch_x, notch_y, notch_x + notch_width, notch_y + notch_height],
                        radius=4,
                        fill='#1a1a1a'
                    )
                    
                    # Home indicator (bottom)
                    indicator_width = 40
                    indicator_height = 4
                    indicator_x = (frame_width - indicator_width) // 2
                    indicator_y = frame_height - frame_thickness - 8
                    draw.rounded_rectangle(
                        [indicator_x, indicator_y, indicator_x + indicator_width, indicator_y + indicator_height],
                        radius=2,
                        fill='#666666'
                    )
                    
                    # Add device info text on screen
                    device_name = device_info.get('DeviceName', 'iOS Device')
                    ios_version = device_info.get('ProductVersion', 'Unknown')
                    model = device_info.get('ProductType', 'Unknown')
                    
                    # Load fonts
                    try:
                        font_large = ImageFont.truetype("arial.ttf", 24)
                        font_med = ImageFont.truetype("arial.ttf", 16)
                        font_small = ImageFont.truetype("arial.ttf", 12)
                    except:
                        font_large = ImageFont.load_default()
                        font_med = ImageFont.load_default()
                        font_small = ImageFont.load_default()
                    
                    # Calculate screen center
                    screen_center_x = screen_x + screen_width // 2
                    screen_center_y = screen_y + screen_height // 2
                    
                    
                    # Main content area
                    draw.text((screen_center_x, screen_center_y - 60), "📱", fill='white', anchor='mm', font=font_large)
                    draw.text((screen_center_x, screen_center_y - 20), device_name, fill='white', anchor='mm', font=font_med)
                    draw.text((screen_center_x, screen_center_y + 10), f"iOS {ios_version}", fill='#a0a0a0', anchor='mm', font=font_small)
                    draw.text((screen_center_x, screen_center_y + 30), model.replace('iPhone', ''), fill='#a0a0a0', anchor='mm', font=font_small)
                    
                    # Bottom message
                    draw.text((screen_center_x, screen_center_y + 80), "Screenshot unavailable", fill='#666', anchor='mm', font=font_small)
                    draw.text((screen_center_x, screen_center_y + 100), "SSL connection issue", fill='#666', anchor='mm', font=font_small)
                    
                    # Add some iOS-style app icons at the bottom
                    icon_size = 20
                    icon_y = screen_y + screen_height - 60
                    icons = ['⚙️', '📷', '📱', '🌐']
                    for i, icon in enumerate(icons):
                        icon_x = screen_x + 30 + i * 35
                        # Icon background
                        draw.rounded_rectangle(
                            [icon_x - 14, icon_y - 14, icon_x + 14, icon_y + 14],
                            radius=7,
                            fill='#333333'
                        )
                        draw.text((icon_x, icon_y), icon, fill='white', anchor='mm', font=font_med)
                    
                    # Convert to PNG bytes
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    device_info['screenshot'] = img_buffer.getvalue()
                    screenshot_captured = True
                    self.log_updated.emit("Created iPhone-style device mockup")
                    
                except Exception as placeholder_error:
                    self.log_updated.emit(f"[WARNING] Could not create placeholder: {placeholder_error}")
                    device_info['screenshot'] = None
                    self.log_updated.emit("[WARNING] No visual representation available")
            
            self.progress_updated.emit(75)
            
            self.progress_updated.emit(100)
            self.device_info_ready.emit(device_info)
            self.task_finished.emit("Device info retrieved successfully.")
            
        except NoDeviceConnectedError:
            self.log_updated.emit("[ERROR] No device connected. Please connect a device and try again.")
            self.task_finished.emit("Failed: No device connected.")
        except InvalidServiceError as e:
            self.log_updated.emit(f"[ERROR] Service not available on device: {e}")
            self.task_finished.emit("Failed: Service not supported by device.")
        except Exception as e:
            self.log_updated.emit(f"[ERROR] Could not get device info: {e}")
            self.task_finished.emit("Failed to retrieve device info.")

    def run_backup(self):
        """Performs a full device backup."""
        try:
            if not self.backup_directory:
                self.log_updated.emit("[ERROR] No backup directory specified.")
                self.task_finished.emit("Failed: No backup directory.")
                return
                
            self.log_updated.emit("Searching for connected devices...")
            self.progress_updated.emit(5)
            
            # Select the first available device
            device = select_device()
            if not device:
                raise NoDeviceConnectedError("No USB devices found")
                
            self.log_updated.emit(f"Found device: {device}")
            self.progress_updated.emit(10)
            
            # Create lockdown client
            self.log_updated.emit("Establishing lockdown connection...")
            lockdown = create_using_usbmux(device.serial)
            self.log_updated.emit("Device connected successfully")
            self.progress_updated.emit(20)
            
            # Get device name for backup folder
            device_name = lockdown.get_value(domain=None, key='DeviceName') or 'Unknown_Device'
            device_name = "".join(c for c in device_name if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # Create timestamped backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_directory, f"{device_name}_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            self.log_updated.emit(f"Creating backup in: {backup_path}")
            self.progress_updated.emit(25)
            
            # Try alternative approach - use command line pymobiledevice3
            try:
                self.log_updated.emit("Attempting backup using pymobiledevice3 command line...")
                self.progress_updated.emit(30)
                
                # Get device UDID for command line
                device_udid = lockdown.get_value(domain=None, key='UniqueDeviceID')
                
                # Construct pymobiledevice3 backup command
                import subprocess
                backup_cmd = [
                    'python', '-m', 'pymobiledevice3', 'backup2', 'backup',
                    '--udid', device_udid,
                    '--full', backup_path
                ]
                
                self.log_updated.emit(f"Running command: {' '.join(backup_cmd)}")
                self.log_updated.emit("This may take several minutes depending on device content...")
                self.log_updated.emit("Note: Device must be unlocked and backup enabled in settings")
                
                # Run the backup command with live output monitoring
                process = subprocess.Popen(
                    backup_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Combine stderr with stdout
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                
                # Monitor the process with live updates
                progress = 50
                output_lines = []
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        output_lines.append(line)
                        
                        # Parse progress from output
                        if "%" in line:
                            try:
                                # Look for percentage patterns
                                import re
                                percent_match = re.search(r'(\d+)%', line)
                                if percent_match:
                                    percent = int(percent_match.group(1))
                                    # Scale to our progress range (50-90)
                                    progress = 50 + int((percent / 100) * 40)
                                    self.progress_updated.emit(progress)
                            except:
                                pass
                        
                        # Update progress based on keywords
                        if "connecting" in line.lower():
                            progress = 55
                        elif "starting" in line.lower() or "began" in line.lower():
                            progress = 60
                        elif "copying" in line.lower() or "backing up" in line.lower():
                            progress = min(progress + 2, 85)
                        elif "finalizing" in line.lower() or "finishing" in line.lower():
                            progress = 88
                        
                        self.progress_updated.emit(progress)
                        self.log_updated.emit(f"BACKUP: {line}")
                
                # Get final return code
                return_code = process.poll()
                stdout = '\n'.join(output_lines)
                stderr = ""
                
                if return_code == 0:
                    self.progress_updated.emit(90)
                    self.log_updated.emit("Command line backup completed successfully!")
                    backup_success = True
                else:
                    self.log_updated.emit(f"Command line backup failed with return code {return_code}")
                    if stdout:
                        self.log_updated.emit(f"Output: {stdout}")
                    backup_success = False
                        
                if not backup_success:
                    # Final fallback - try API one more time with just path
                    try:
                        backup_service = Mobilebackup2Service(lockdown)
                        self.log_updated.emit("Trying final API backup attempt...")
                        backup_service.backup(backup_path)
                        backup_success = True
                        self.log_updated.emit("Final API backup successful")
                    except Exception as final_error:
                        self.log_updated.emit(f"Final API backup failed: {final_error}")
                        raise Exception("All backup methods failed. This device may not support programmatic backup or requires iTunes/Finder to be configured first.")
                
                self.progress_updated.emit(90)
                self.log_updated.emit("Backup completed successfully!")
                self.log_updated.emit(f"Backup saved to: {backup_path}")
                
                # Get backup size
                try:
                    backup_size = self._get_directory_size(backup_path)
                    self.log_updated.emit(f"Backup size: {self._format_size(backup_size)}")
                except:
                    pass
                
                self.progress_updated.emit(100)
                self.task_finished.emit(f"Backup completed successfully in {backup_path}")
                
            except InvalidServiceError:
                self.log_updated.emit("[ERROR] Backup service not available on this device.")
                self.log_updated.emit("Device may need to be unlocked or backup service disabled.")
                self.task_finished.emit("Failed: Backup service not available.")
            except Exception as backup_error:
                self.log_updated.emit(f"[ERROR] Backup process failed: {backup_error}")
                self.task_finished.emit("Backup failed during process.")
                
        except NoDeviceConnectedError:
            self.log_updated.emit("[ERROR] No device connected. Please connect a device and try again.")
            self.task_finished.emit("Failed: No device connected.")
        except Exception as e:
            self.log_updated.emit(f"[ERROR] Backup failed: {e}")
            self.task_finished.emit("Backup failed.")
    
    def _get_directory_size(self, directory):
        """Calculate total size of directory in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    pass
        return total_size
    
    def _format_size(self, size_bytes):
        """Format bytes as human readable size."""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _create_device_frame(self, screenshot_data):
        """Create an iPhone-like frame around a screenshot."""
        try:
            # Load the screenshot
            screenshot_img = Image.open(io.BytesIO(screenshot_data))
            
            # iPhone frame dimensions
            frame_thickness = 20
            corner_radius = 25
            frame_width = screenshot_img.width + (frame_thickness * 2)
            frame_height = screenshot_img.height + (frame_thickness * 2) + 60  # Extra space for notch
            
            # Create frame image
            framed_img = Image.new('RGBA', (frame_width, frame_height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(framed_img)
            
            # Draw iPhone frame
            frame_color = '#2c2c2c'
            draw.rounded_rectangle(
                [0, 0, frame_width, frame_height], 
                radius=corner_radius, 
                fill=frame_color, 
                outline='#404040', 
                width=2
            )
            
            # iPhone notch
            notch_width = 60
            notch_height = 8
            notch_x = (frame_width - notch_width) // 2
            notch_y = frame_thickness + 5
            draw.rounded_rectangle(
                [notch_x, notch_y, notch_x + notch_width, notch_y + notch_height],
                radius=4,
                fill='#1a1a1a'
            )
            
            # Home indicator
            indicator_width = 40
            indicator_height = 3
            indicator_x = (frame_width - indicator_width) // 2
            indicator_y = frame_height - frame_thickness - 8
            draw.rounded_rectangle(
                [indicator_x, indicator_y, indicator_x + indicator_width, indicator_y + indicator_height],
                radius=2,
                fill='#666666'
            )
            
            # Paste screenshot into frame
            screen_x = frame_thickness
            screen_y = frame_thickness + 30
            framed_img.paste(screenshot_img, (screen_x, screen_y))
            
            # Convert back to bytes
            img_buffer = io.BytesIO()
            framed_img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
            
        except Exception as e:
            # If framing fails, return original screenshot
            return screenshot_data

# --- Main Application GUI ---
class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()
        self.apply_stylesheet()
        self.connect_signals()
        self._on_command_changed()

    def setup_ui(self):
        self.setWindowTitle("iOS Backup & Info Tool")
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 700, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Main Title and Subtitle
        title_label = QLabel("iDevice Manager")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("Local backup and information utility for Apple devices")
        subtitle_label.setObjectName("subtitleLabel")
        main_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(10)

        # Action Controls
        controls_group = self._create_controls_group()
        main_layout.addWidget(controls_group)
        
        # Device Info Panel (initially hidden)
        self.device_info_group = self._create_device_info_group()
        main_layout.addWidget(self.device_info_group)
        self.device_info_group.setVisible(False)

        # Log and Progress
        log_group = self._create_log_group()
        main_layout.addWidget(log_group)
        main_layout.setStretchFactor(log_group, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)
        
    def _create_controls_group(self):
        group = QGroupBox("Select Action")
        layout = QVBoxLayout()
        
        self.command_combo = QComboBox()
        self.command_combo.addItems(["Get Device Info", "Create Full Backup"])
        layout.addWidget(self.command_combo)

        # Backup directory selection (initially hidden)
        self.backup_dir_layout = QHBoxLayout()
        self.backup_dir_label = QLabel("Backup Directory:")
        self.backup_dir_input = QLineEdit()
        self.backup_dir_input.setPlaceholderText("Select backup destination...")
        self.backup_dir_input.setReadOnly(True)
        self.backup_dir_button = QPushButton("Browse...")
        self.backup_dir_button.clicked.connect(self._select_backup_directory)
        
        self.backup_dir_layout.addWidget(self.backup_dir_label)
        self.backup_dir_layout.addWidget(self.backup_dir_input, 1)
        self.backup_dir_layout.addWidget(self.backup_dir_button)
        
        # Create widget to hold backup directory controls
        self.backup_dir_widget = QWidget()
        self.backup_dir_widget.setLayout(self.backup_dir_layout)
        self.backup_dir_widget.setVisible(False)
        layout.addWidget(self.backup_dir_widget)

        # Action button setup
        self.action_button = QPushButton("Get Info")
        self.action_button.setObjectName("ActionButton")
        layout.addWidget(self.action_button)
        
        group.setLayout(layout)
        return group

    def _create_device_info_group(self):
        """Creates the panel to display the screenshot and device data."""
        group = QGroupBox("Device Information")
        main_layout = QHBoxLayout()

        # Left side: Screenshot
        self.screenshot_label = QLabel("Connect a device and\nclick 'Get Info'")
        self.screenshot_label.setFixedSize(200, 400)
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_label.setWordWrap(True)
        self.screenshot_label.setObjectName("screenshotLabel")
        self.screenshot_label.setStyleSheet(
            "QLabel { border: 2px solid #555; border-radius: 8px; background-color: #2b2b2b; }"
        )
        main_layout.addWidget(self.screenshot_label)

        # Right side: Formatted Data
        self.info_layout = QFormLayout()
        self.info_layout.setContentsMargins(10, 0, 0, 0)
        self.info_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.info_layout.setSpacing(10)
        
        main_layout.addLayout(self.info_layout)
        main_layout.setStretchFactor(self.info_layout, 1)
        
        group.setLayout(main_layout)
        return group
        
    def _create_log_group(self):
        group = QGroupBox("Log Output")
        layout = QVBoxLayout()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)
        group.setLayout(layout)
        return group
    
    def connect_signals(self):
        self.action_button.clicked.connect(self.start_task)
        self.command_combo.currentIndexChanged.connect(self._on_command_changed)

    def _on_command_changed(self):
        command = self.command_combo.currentText()
        if command == "Get Device Info":
            self.action_button.setText("Get Device Info")
            self.backup_dir_widget.setVisible(False)
        else:
            self.action_button.setText("Start Full Backup")
            self.backup_dir_widget.setVisible(True)
    
    def start_task(self):
        command_map = {
            "Get Device Info": "device-info",
            "Create Full Backup": "backup"
        }
        command = command_map[self.command_combo.currentText()]
        
        if command == 'device-info':
            # Hide old info and logs to show we're working
            self.device_info_group.setVisible(False)
            self.log_box.clear()
        elif command == 'backup':
            # Check if backup directory is selected
            if not self.backup_dir_input.text():
                QMessageBox.warning(self, "No Backup Directory", 
                                  "Please select a backup directory before starting backup.")
                return
            self.log_box.clear()
            
        self._set_controls_enabled(False)
        
        backup_directory = self.backup_dir_input.text() if command == 'backup' else None
        self.worker = TaskWorker(command, backup_directory)
        self.worker.log_updated.connect(self.update_log)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.task_finished.connect(self._on_task_finished)
        self.worker.device_info_ready.connect(self._on_device_info_ready)
        self.worker.start()

    def _on_device_info_ready(self, info: Dict):
        """Slot to handle the retrieved device info and display it."""
        # Update screenshot
        if info.get('screenshot'):
            pixmap = QPixmap()
            pixmap.loadFromData(info['screenshot'])
            scaled_pixmap = pixmap.scaled(
                self.screenshot_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.screenshot_label.setPixmap(scaled_pixmap)
        else:
            # Show placeholder text if no screenshot available
            self.screenshot_label.clear()
            self.screenshot_label.setText("Screenshot not\navailable for\nthis device")
        
        # Clear old data from QFormLayout
        while self.info_layout.count():
            self.info_layout.removeRow(0)
            
        # Add new data with better formatting
        device_fields = [
            ('Name:', info.get('DeviceName', 'N/A')),
            ('iOS Version:', info.get('ProductVersion', 'N/A')),
            ('Build:', info.get('BuildVersion', 'N/A')),
            ('Model:', info.get('ProductType', 'N/A')),
            ('Serial Number:', info.get('SerialNumber', 'N/A')),
            ('UDID:', info.get('UniqueDeviceID', 'N/A')[:8] + '...' if info.get('UniqueDeviceID') else 'N/A')
        ]
        
        for label, value in device_fields:
            label_widget = QLabel(f"<b>{label}</b>")
            value_widget = QLabel(str(value))
            value_widget.setWordWrap(True)
            self.info_layout.addRow(label_widget, value_widget)
        
        self.device_info_group.setVisible(True)

    def _on_task_finished(self, message):
        QMessageBox.information(self, "Task Completed", message)
        self._set_controls_enabled(True)
        self.worker = None

    def update_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format different message types with colors and icons
        if message.startswith("[ERROR]"):
            formatted_message = f"🔴 {timestamp} | {message}"
            color = "#ff6b6b"
        elif message.startswith("[WARNING]"):
            formatted_message = f"🟡 {timestamp} | {message}"
            color = "#ffd93d"
        elif "successfully" in message.lower() or "completed" in message.lower():
            formatted_message = f"✅ {timestamp} | {message}"
            color = "#51cf66"
        elif "starting" in message.lower() or "attempting" in message.lower():
            formatted_message = f"🔄 {timestamp} | {message}"
            color = "#74c0fc"
        elif "found device" in message.lower():
            formatted_message = f"📱 {timestamp} | {message}"
            color = "#91a7ff"
        elif "connecting" in message.lower() or "establishing" in message.lower():
            formatted_message = f"🔗 {timestamp} | {message}"
            color = "#ffd43b"
        else:
            formatted_message = f"ℹ️  {timestamp} | {message}"
            color = "#ffffff"
        
        # Apply color formatting
        self.log_box.appendPlainText(formatted_message)
        
        # Scroll to bottom
        scrollbar = self.log_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def _select_backup_directory(self):
        """Open file dialog to select backup directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Backup Directory",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.backup_dir_input.setText(directory)
    
    def _set_controls_enabled(self, enabled):
        self.action_button.setEnabled(enabled)
        self.command_combo.setEnabled(enabled)
        self.backup_dir_button.setEnabled(enabled)
        
    def apply_stylesheet(self):
        """Apply a modern dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            #titleLabel {
                font-size: 24pt;
                font-weight: bold;
                color: #ffffff;
                margin: 10px;
            }
            
            #subtitleLabel {
                font-size: 11pt;
                color: #a0a0a0;
                margin-bottom: 20px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12pt;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #888;
            }
            
            QPlainTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
                line-height: 1.4;
                padding: 8px;
                selection-background-color: #3d5afe;
            }
            
            QProgressBar {
                border: 1px solid #555;
                border-radius: 8px;
                text-align: center;
                background-color: #2b2b2b;
                font-weight: bold;
                font-size: 10pt;
                height: 25px;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4CAF50, stop: 1 #45a049);
                border-radius: 7px;
                margin: 1px;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Show license agreement dialog first
    license_dialog = LicenseDialog()
    if license_dialog.exec() != QDialog.DialogCode.Accepted:
        # User declined the license, exit the application
        sys.exit(0)
    
    # User accepted the license, proceed with main application
    window = BackupApp()
    window.show()
    sys.exit(app.exec())