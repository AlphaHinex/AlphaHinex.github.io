---
id: connection-pools-1
title: "​Real-World Performance - 13 - Large Dynamic Connection Pools - Part 1"
description: "We actually got quite tired of talking to people about this."
date: 2021.08.29 10:34
categories:
    - Database
tags: [Connection Pools]
keywords: dynamic connction pools, static connection pools, fixed connection pools 
cover: /contents/covers/connection-pools-1.png
---

https://mp.weixin.qq.com/s/D2PUOwAE93eHJpfYXARoXA

Today we are going to talk about connecting to the database and

how we choose connect to the database.

In previous YouTube videos, we've shown
how

developers might connect to the database,
and how they would use

cursors and arrays, and things like that. But we are going to do a

topic that really should be thought about from both the system administrator

and the system architect. And it's the number of connections that we make to the database

and how they connect to the database. Are
those connections permanent

or are they dynamic? This is a topic that my colleagues within the Real World Performance group

have been dealing with for
probably the best part of 20 years.

And basically

it's done wrong in many cases, and it's
usually done wrong

because of over-optimistic views

of how they think the database can just
keep on

absorbing more and more connections. The reality of the situation is

that there's two things at stake here. One the database--you cannot add

an infinite number connections to the
database. And

the second thing is the number of
connections to the database should ideally

be static--should be the same number all
time.

Unfortunately, today's applications
tend to get built in middle tiers

and they tend to specify dynamic
connection pools. Very often it's a

minimum number and then maximum number.

And there's under.... people are under this illusion that basically

the applications servers will keep on
creating connections as required,

and they'll potentially cut them back if the load goes off.

Well in fact this is actually the worst
thing possible to do.

In fact, one of my colleagues often defines this sort of architecture

as a "gun ready to go off." You have the
potential to rapidly create a large

number

connections. We have the ability to
basically

destabilize the entire database
environment.

And for this reason itself, um,

we actually got quite tired of talking to
people about this.

And for this reason we built demos and
we

built graphical screens to actually show
what happens

when the load comes on the system. So to
demonstrate the

the challenges associated with both a
large connection pool and a

dynamic connection pool, what we're going to do is we are going to simulate load coming on a system

in slow motion. So we can actually

watch and interrogate a system  as the load comes up.

The reasoning being for that is that if we see in slow motion



we can actually see what is happening
and watch the system fall apart in



front of you rather than it all
happening in two seconds



and system just falling over and everyone
curious as to what has happened.



And this it becomes particularly
important



to understand what is happening and how
quickly these things



can run out of control. So and



we're back using the Real World Performance demo screens



and you'll notice we have basically



three windows down the middle which is
reporting what we're doing. Now we have a



very stable system here,



running at this point in time. You can
notice that the response time from the



applications



is two milliseconds. We're running at
quite a modest transaction rate of just



under 2,000 transactions a second.



But let's talk about what our user
community is doing. What we actually have



is nearly 15,000 individual Java threads



all playing effectively cards online.



And they're



basically pressing the button,
each thread, once every 10 seconds.



What we've done is we've created a
connection pool that can



literally go out of control and destabilize
the system.



The initial connection pool was a 144
connections to the database, but we're going



let it grow



to 6,000 connections to the database



when the load comes on. Now if we look at the system at the moment you can see we're



barely recording anything on the AWR
report or ASH reports.



The CPU utilization is extremely low.



And the other thing to notice is that
even though the



utilization on the system is extremely
low, we've already



extended the connection pool at over 200
connections to the database



up from 144, just because the
application servers



occasionally found that all their connections were busy, we allowed it to grow.



And with that in mind and I'm going to



force it to grow even more. And we are going to watch the system as we start to grow.



So I'm going to start doubling up the work load, so instead of everyone



pressing the button every 10 seconds,
we are now going to make it every five seconds.



And we'll double this up.



And I'm going to continue to double this up until it gets quite



interesting and we've actually started to make the system yield.



At this point just doubling up the
workload, you can see that there's just a



tiny



increment in the workload, the transaction
rate is doubling,



the response time hasn't been impacted
it all,



we're starting to see a little bit of climb on
the CPU utilization,



which we can see we're barely even using
seven or eight



percent of the system this point in time. So let's double it up



in another step.



And again, here we go doubled up the
workload again. And



at this point in time, we can see very
linear behavior



on the system. We're seeing the
transaction rate literally



double with each step. We're barely
impacting



response time. And we're seeing the CPU getting proportional response



coming up as the workload comes up.



So, at this point in time, people will
start to think we've built a linear and



a scaleable system. The other thing to note



is that we are starting to see the connections to the database



and the size of the connection pool now is now approaching nearly 500, okay.



So we are really about four times bigger



nearly five times bigger than the
initial connection pool,



yet we've hardly stretch the machine at all.



So there's a lot of connections that
actually aren't doing anything



in fact



is 465 at this point in time, where we are not actually doing anything at all.



We've only got 16 active. And this is on a
machine here



with actually twenty four cores on. So
you can see we're



not even fully utilizing the machine in
terms of sessions per



core at this point. But you can see, again,



that connection count is increasing just
because you get occasional



timing glitches where of all the 32
JVMs that



we have driving this application, all the
connections are



busy for one point in time and so we just
popped another connection.



So let's double up the workload a little
bit more, and then we should start



getting into start seeing



load come onto the system a little bit
more seriously.



So we're doubling it up now,



and we are starting to push the transaction
rate



much higher. We are getting up into the
15-16



thousand transactions per second. Thing
to note here, you starting to see a much



more



noticeable increase in the CPU on the
system,



and we're approaching at this point 25
percent utilization on the system.



But again nothing to see in database on
ASH report,



not much to see of the user response time.
This is the point in time



where very often we see system architects and administrators



congratulating each other because they
think, "wow we've got this 



scaleable system."  But it's only
scaleable to 



25 percent utilization of the database server. That's



hardly the best utilization of hardware
resources,



software licenses. So let's double up
again



and see where get to when we start. Hopefully, now that we're going to get



to use 50 percent of the utilization on the
machine.



So we're doubling up again and we can
see,



again, a very immediate response. The
transaction rate is doubling.



We are seeing the CPU workload doubling. And we're nearly at



50 percent utilization on the system.
Barely an increase on the system



response time. Again a very stable system.



The thing to note now is we really are
starting to grow a lot more connections to the



database,



is the middleware is now getting to
situation. It is running at a higher rate



and the statistical chance that all the
connections used from one JVM



being in use is increasing all the time. So literally as I've been speaking, we're seeing the



connections pop to



over nearly 2000 here. We are at 1900



as I spoke, before we were in the
hundreds,



and within a second or so, I imagine we are going to be



greater than 2000 fairly quickly. But you can see quite quickly that



you know, still at this point in time the
system is very predictable,



very linear, and everyone seeming great. And this is at the point where



we're about fifty percent utilization on the system.



Now at fifty percent utilization on the
system,



we can see this is a point where our
statistical chance of getting scheduled



is 2 in 1. As I crank up the
utilization on the system,



your chance of getting scheduled
immediately



is starting to get reduced. We are starting to not get scheduled all of the



time. We are going to start seeing more variation in the response time.



As the response time varies, we are more likely to have



more application servers waiting.



And they are more likely to initiate more
connections.



So you can see as we crank up the
utilization



we can more likely to basically get more
variable response time,



which is going to force the app servers
to throw more connections at the database,



which in its turn, are going to get more and more unpredictable response time,



and we're get ourselves in what is known as a race condition. And this race condition we 



very often call a connection
storm, when basically we're initiating a



storm of  connection requests but we are actually getting 



nothing back. And remember what was shown in previous YouTubes



the actually logging on and off the database is quite an expensive operation.



So this just compounds this effect, and we start going into a spiral of degrading



performance.



So I'm going to not double the performance at this point in time.



Because as you can see it's been quite well behaved. We've got over



2000 connections to the database at this
point. But what we're going to do this we do



is we are going to do it in smaller increments.



So instead of doubling it, I'm just gonna



take it up to four hundred milliseconds, so 
0.4 percent of a second between each mouse clicks.



So



some fairly serious card players. And



we are just going to jump the workload up a little bit more.



And you can see that basically, suddenly the small increment in work suddenly



caused



quite an impact on the system, okay?



So almost like a 50 percent increase in the
workload, we saw almost



twice as much CPU. We see this disproportional response in CPU utilization



getting extremely busy. We're not seeing
proportional



increase in the transaction rate, and
we're now starting to see the



transaction rate



starting to become quite choppy. And we are starting to see



queuing in the middle tier machine. And we're seeing extended database response times.



And for the first time, we are actually starting to see wait events



inside the database through the ASH
reports.



And some of you may have seen some of these



wait events in your life before. Latches on end queues,



row cache objects, latch free 



enq:TX index contention, buffer busy waits.



Quite common wait events as and well, we getting to the situation where we're  starting to



oversubscribe the machine, but the CPU
is starting to get extremely busy.



And we're starting to see more and more wait events. We are starting to see the CPU get busier



and busier.



And you can see now that the database
connection pool



that was at 2000 is now approaching 6000.



Remember we have a limit here of 6144.



So very quickly, we're actually getting
to the situation where we are approaching our



connection limits.



And you'll notice the number of active connections on the database



is massively oversubscribed, compared to
the number



of cores on the system. It's now telling me I have



6,000 active requests into the database



at this point in time. As a result you can
actually see



we've completely oversubscribed the machine so the response time



has gone out of control, the wait event 
inside the database has gone



completely out of control. Just
looking at that you can see



enq:TX index contention, contention events



and the throughput is dropped right off.



And in fact what we're starting to see
is the monitoring of the thing



is starting to become unpredictable. And
even in fact the CPU has dropped off



because this machine has now actually rendered itself completely unstable.



And at this point in time, we've
actually



simulated a failure in the system.



And then sometimes it starts to recover and it's erratically



you can see the trajectory sometimes
bounce-back, but



effectively what we've done is hang
the system.



And trying to use a keyboard and things like this



becomes impossible. So getting debugging
information on such a system



into this state becomes next to
impossible.

