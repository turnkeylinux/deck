<?xml version="1.0" encoding="UTF-8"?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="0" left="573" height="933" width="701"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="zaril.20100820190533" a="E"><vh>Project</vh>
<v t="zaril.20100820190533.1" a="E"><vh>design</vh>
<v t="zaril.20100820193236"><vh>brainstorming</vh></v>
<v t="zaril.20100820223439"><vh>terminology</vh></v>
<v t="zaril.20100820192834"><vh>file/data structure</vh></v>
<v t="zaril.20100820191018" a="E"><vh>cli syntax + psuedo-logic</vh></v>
</v>
<v t="zaril.20100820224228" a="E"><vh>implementation</vh>
<v t="zaril.20100820230804" a="M"><vh>fix useraufs to allow usage by root, limited to certain directories</vh></v>
<v t="zaril.20100821001344" a="M"><vh>deck a filesystem path</vh></v>
<v t="zaril.20100821001344.2" a="M"><vh>delete a deck</vh></v>
<v t="zaril.20100822052346" a="M"><vh>refactor deck storage into a separate class</vh></v>
<v t="zaril.20100821001344.1" a="M"><vh>deck a deck</vh></v>
<v t="zaril.20100821001344.3" a="E"><vh>get fstab functionality to work</vh>
<v t="zaril.20100823052232"><vh>gotcha: binds don't show up as binds in /proc/mounts</vh></v>
<v t="zaril.20100822094316"><vh>security gotcha: mounting requires CAP_SYS_ADMIN privileges</vh></v>
<v t="zaril.20100823064145"><vh>security gotcha: root could edit fstab and "trick" deck into arbitrary mounts</vh></v>
</v>
<v t="zaril.20100821001344.4"><vh>update deck fstab</vh></v>
<v t="zaril.20110111140920"><vh>isdirty</vh></v>
<v t="zaril.20110111140920.1" a="TV"><vh>deck --get-level</vh></v>
</v>
<v t="zaril.20101112070401" a="E"><vh>todo/wishlist</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="zaril.20100820190533">@nocolor
</t>
<t tx="zaril.20100820190533.1"></t>
<t tx="zaril.20100820191018">deck src dst
	create a new deck
	src can be a regular file path or another deck

deck dst
	setup an existing deck

deck -D dst
	works if dst is mounted or not
	unmounts dst
	removes the directory
	removes the stack
	removes all structures with a ref count of zero

deck -r dst
    refresh mounts of dst

deck -t dst
    test if path is a deck

example usage:
    deck / deckedroot
    deck deckedroot
    deck deckedroot fooroot</t>
<t tx="zaril.20100820192834">

.deck/
    levels.refs/ # references to overlay levels
        &lt;level-id&gt;/
            &lt;name&gt; -&gt; ../stacks/&lt;name&gt;
    
    levels # overlay levels
        &lt;level-id&gt;/ # &lt;level-id&gt; is a random hash
            
    stacks/ # stack structure of decks (which levels in what order)
        &lt;name&gt;/
            0 -&gt; /base
            1 -&gt; ../../levels/3902bf6c37bdd2d16d92731ed76400ab 
            2 -&gt; ../../levels/0944b20f5eceec96a2da758182e8516e
    
        &lt;name-derivative&gt;/
            0 -&gt; /base
            1 -&gt; ../../levels/3902bf6c37bdd2d16d92731ed76400ab
            2 -&gt; ../../levels/5b04f8c439460a60b200393c1604d5cc

    mounts/ # pointers to a record of mounts for this deck (if we're root)
        &lt;name&gt;
	&lt;name-derivative&gt;
</t>
<t tx="zaril.20100820193236">Q: how do I name this project?

alternatives
    veneer
    cover
    layer
    snapshot (from vmware)
    facade
    fs prefix
    datalayer
    filelayer
    parallel universe
    alternate   
    ride
    pile
    stack
    raise
    climb
    stack
    branch
    deck (*)

A:
    deck

advantages:
    deck of cards
    decks of a ship
    short
    pronouncable
    unique
        no existing command
        unambigious
    sounds good as an action (deck it)

* DESIGN IDEAS
    instead of remounting altered decks just inject a new overlay

    use symbolic links to represent copied overlays

    identify bind mounts and replicate them
        would replicate /proc and /sys mounts in a decked chroot
    
* QUESTIONS
Q: what would happen to unmounted decks?
A:
	they would be remounted with the existing overlays?
---
Q: how do we name the overlays?
A:
	an id?
		pros
			easy to implement
		cons
			might be confused with union stacking order
			we'll have to list the branches directory
	random?
		hard to generate?

	time/date based?
		&lt;name&gt;-&lt;date&gt;

	&lt;date&gt;
		guarantee uniqueness by checking for existence?
			append with modifier

		does it really matter when a branch was created?\
			it'll just make for difficult typing

		let the creation time be a property of the directory

	hash of whatever
---	
Q: why was it that useraufs didn't support root?
A:
    because it was equivalent to mount --bind which could be used by root to get around the MAC policy
---
Q: should deck allow a user to deck a root owned filesystem?
	if its readonly why do we care?
		I.e., the user would have had access to that directory
A:		no, because it would allow you to bypass grsecurity restrictions
---
Q: what changes do we need to make to useraufs to support both root and users?
A:
    limit root useraufs to specific directories
---
Q: what happens when we branch from a deck?
A:
    we clone the deck structure, and add an overlay to both the original and new deck
    if the original deck is mounted, 
        remount the last level as readonly
        insert the last overlay as writeable
---
GOTCHA: cross directory decking introduces multiple problems
    potential namespace conflicts
        same deck name in two different directories
            breaks assumptions of file structure

    if linked decks move, this could break the deck
        absolute level links would no longer be correct

    increases complexity significantly

IDEAS:
    redesign internals for storage in one big deck (global $HOME/.deck)

    disallow cross-directory decking

    support `decking' by cloning the origin deck into local deck?
        I.e., with rsync
            clone hardlinks if possible

do we really need to allow cross-project decking?
    what is the use?
    this design makes the derivatives more visible

Q: what would the file format for a global design look like?
A:
    
.deck/
    levels.refs/
        &lt;level-id&gt;/
            &lt;hash-of-filepath&gt; -&gt; ../decks/&lt;hash-of-filepath&gt;
    
    levels/
        &lt;level-id&gt;/
            &lt;level-id&gt; := &lt;hash&gt; 
                generated from &lt;name&gt;-&lt;time&gt;
                if it exists, create another one
            
    decks/
        &lt;hash-of-filepath&gt;/
            0 -&gt; /base
            1 -&gt; ../../levels/&lt;level-id&gt;
            2 -&gt; ...

            fstab
    
alternative?
        file/path/
            0 -&gt;
            1 -&gt; 
            2 -&gt; 

cons:
    more opaque file structure
    that a deck is a deck is not clear (no .deck directory)
    immobile decks
    different users would have different global storage
        e.g., root couldn't deck a user's filesystem

---
IDEA: rename 0 node the root node?
    differentiate between levels and the root filesystem...

    </t>
<t tx="zaril.20100820223439">deck
    a virtual filesystem branch derived from a directory or another deck

stack
    a stack of filesystem levels a deck is comprised of

levels
    behind the scenes, decks are a union of multiple filesystem levels
</t>
<t tx="zaril.20100820224228">ROADMAP/MILESTONES

    </t>
<t tx="zaril.20100820230804">useraufs already supports allow_user allow_dir directives

We just have to change useraufs so it rejects root by default, but allow root if specified 
by the allow_user directive.


</t>
<t tx="zaril.20100821001344">deck /path/to/directory deck1

create(src, dst)
    raise exception if src isn't a directory
    raise exception if dst has already been initialized or is not an empty directory

    calculate level id
    create a new level
    create the deck structure
    create the reference
</t>
<t tx="zaril.20100821001344.1">deck /path/to/deck1 deck2

create logic in DeckStorage:
    if source_path is a deck:
        exception if deck source is not in the same directory as the desk destination
    
        copy the root of the source deck
        for every level:
            add that level to the new deck and increase its reference count
        add a new level to the source deck
        add a new level to the destination deck
    
logic in Deck:
    when we add a level if its mounted then we need to
    
handle non-decks

TESTS
    try decking a deck from another directory
    try decking an unmounted deck
    try decking a mounted deck
</t>
<t tx="zaril.20100821001344.2">deck -d deck1

logic
    unmount the deck
    delete stack
    delete any references
        if references hit zero, delete level
</t>
<t tx="zaril.20100821001344.3">will save sub-mounts in fstab and replicate them

design
    mounts object 
        init can read from file and adjust/filter only mounts matching a path
        can write internal state to file
        can apply mounts to another directory  

create logic
    if source is a deck, copy it's mount as the initial value
    if the source_path has submounts, create a new fstab


MILESTONES
    I deck a chrooted directory, it creates an fstab for chroot and mounts it on the deck
    onl y if we're root
    delete the mounts



Q: what is the format of fstab?
A:
&lt;device | filesystem&gt;    &lt;mountpoint&gt;    &lt;type&gt;  &lt;opts&gt;
---
Q: does /proc/mounts follow fstab format?s
A: yes
---
GOTCHA: binds don't show up as binds in /proc/mounts
    SOLUTION: they show up on /etc/mtab
---
GOTCHA: umount failing to umount binds
    SOLUTION: umount in reverse, that way we umount sub-binds (/turnkey/repository) before the parent bind (/turnkey)


</t>
<t tx="zaril.20100821001344.4">deck -u deck2
    will update sub-mounts in fstab</t>
<t tx="zaril.20100822052346">IDEA: we might have multiple storage drivers

Deck is the front-end class
Q: what is the name of the back-end class?

DeckEngine
DeckInternals
DeckBackEnd
DeckDriver
DeckStorage (*)
</t>
<t tx="zaril.20100822094316">we can only apply mounts if we're root AND if we have CAP_SYS_ADMIN privileges

IDEAS:
disable fstab options for regular users
we could give these privileges specially to deck 
can we rely on useraufs to limit root?
    we can't because root might trick us into running another useraufs program
        via PATH for example
        and then we would mount --bind arbitrary filesystems arbitrary places
disable decking from /?
maybe another special wrapper?
maybe a configuration file like useraufs?
    limit which sources we can deck

SOLUTION:
rely on useraufs to decide whether root is allowed or not to deck a certain dir
if useraufs fails, we raise an exception and don't do any dangerous mounting
to prevent deck from being spoofed into running another useraufs program
    hack execproxy to clean_environ() regardless of suid status
        because we are being given special privileges in the MAC policy</t>
<t tx="zaril.20100823052232">E: mount --bind foo bar
    Q: does /proc/mounts contain enough info to reconstruct bind?
    A: no

DISCOVERY: /etc/mtab does contain enough info
</t>
<t tx="zaril.20100823064145">IDEAS
    prevent anything other than root from accessing the chroot's deck
    we'd have to prevent access to ANY directory in which we allow chroots
    make deck sign the fstab? (hide the key)
    store fstab in a different global storage
        we only need to support root anyhow
        then you only give deck permissions to access that directory

SOLUTION:
    develop a key based storage repository
        objects accessed and written by a random key-id

    instead of storing the fstab content in the deck, we store the key
    interface identical to file()
        only instead of a filepath, you have a key


    what do we call it?
        anonfile

        
</t>
<t tx="zaril.20101112070401">list fstab for a given deck

handle deck umounts correctly
    if umounting fails, we should remount them







</t>
<t tx="zaril.20110111140920">--isdirty
    returns true if deck is dirty 
        if last layer has been written to

    deck --isdirty path/to/deck

* LOGIC

listdir the level, and remove built-in entries:
    .wh..wh.aufs 
    .wh..wh.plink

if its still empty, its empty
</t>
<t tx="zaril.20110111140920.1">--get-level last path/to/deck
set last on stacks

* IDEAS
deck --option path/to/deck
    
    deck --path path/to/deck -1
    
    alternatives
        showpath
        show
        info
        path
    
    guts
    getpath
    getstack

    getlevel



    
    </t>
</tnodes>
</leo_file>
