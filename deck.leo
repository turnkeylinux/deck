<?xml version="1.0" encoding="UTF-8"?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="0" left="470" height="933" width="800"/>
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
<v t="zaril.20100820230804"><vh>fix useraufs to allow usage by root, limited to certain directories</vh></v>
<v t="zaril.20100821001344" a="TV"><vh>deck a filesystem path</vh></v>
<v t="zaril.20100821001344.1"><vh>deck a deck</vh></v>
<v t="zaril.20100821001344.2"><vh>delete a deck</vh></v>
<v t="zaril.20100821001344.3"><vh>get fstab functionality to work</vh></v>
<v t="zaril.20100821001344.4"><vh>update deck fstab</vh></v>
</v>
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

deck -d dst
	works if dst is mounted or not
	unmounts dst
	removes the directory
	removes the struct
	removes all structures with a ref count of zero

deck -u dst
    updates mounts of dst

example usage:
    deck / deckedroot
    deck deckedroot
    deck deckedroot fooroot</t>
<t tx="zaril.20100820192834">.deck/
    levels.refs/
        &lt;level-id&gt;/
            &lt;name&gt; -&gt; ../decks/&lt;name&gt;
    
    levels
        &lt;level-id&gt;/

            &lt;level-id&gt; :=
                &lt;hash&gt; (generated from &lt;name&gt;-&lt;time&gt;)
                    if it exists, create another one
            
    decks/
        &lt;name&gt;/
            0 -&gt; /base
            1 -&gt; ../../levels/&lt;level-id&gt;
            2 -&gt; ...

            fstab
    
        &lt;name-derivative&gt;/
            0 -&gt; /base
            1 -&gt; ../../levels/&lt;level-id&gt;
            2 -&gt; ...
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
Q: what would happen to unmounted alts?
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
</t>
<t tx="zaril.20100820223439">deck
    a virtual filesystem branch derived from a directory or another deck

levels
    behind the scenes, decks are a union of multiple filesystem levels
</t>
<t tx="zaril.20100820224228">ROADMAP/MILESTONES

    </t>
<t tx="zaril.20100820230804">useraufs already supports allow_user allow_dir directives

We just have to change useraufs so it rejects root by default, but allow root if specified 
by the allow_user directive.


</t>
<t tx="zaril.20100821001344">deck /path/to/directory deck1</t>
<t tx="zaril.20100821001344.1">deck /path/to/deck1 deck2</t>
<t tx="zaril.20100821001344.2">deck -d deck1</t>
<t tx="zaril.20100821001344.3">will save sub-mounts in fstab and replicate them</t>
<t tx="zaril.20100821001344.4">deck -u deck2
    will update sub-mounts in fstab</t>
</tnodes>
</leo_file>
