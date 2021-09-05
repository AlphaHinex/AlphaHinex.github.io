---
id: connection-pools-2
title: "​Real-World Performance - 14 - Large Dynamic Connection Pools - Part 2"
description: "It's quite dramatic. The only thing I have changed is ..."
date: 2021.09.05 10:34
categories:
    - Database
tags: [Connection Pools]
keywords: dynamic connction pools, static connection pools, fixed connection pools 
cover: /contents/covers/connection-pools-2.png
---

https://mp.weixin.qq.com/s/y_AYQvGUvpSBtewbGEvqcQ

Okay, so now having rendered the system
completely unstable



and unproductive, we got to rescue the
situation. At this point in time is



usually



a lot of corporate blame-game playing
and



usually the users are complaining.



And the application team are blaming the
database, and the database are blaming the



operating system.



And when in fact, really, this is a
challenge



one of architecture. So



at this point in time usually people
saying either "I want more connections to



the database," 



or the database team saying, "I want less
connections to the database." So at this



point in time, what I'm gonna do



is reduce the number of connections down
to a third



what we had, which was just six thousand. Let's do that and actually see what actually



happens. At this point in time, we



we've totally lost the system, so at this
point in time, we're going to rebuild the



connection pool.



And it's going to take a little while, and this is a lesson to be learned.



The fact it takes a while to rebuild a
large connection pool and tear it down.



This is what happens when we have to do
a failover. So



if you were to be designing a system
architecture would you design an



architecture with lots of moving parts,



that need to be reestablished and failed over? That's something we need to consider



when we design architecture for
high-performance



as well as high architecture. Does it
have the capability



to failover quickly?  Okay, so you can see
that we've



recovered the system and actually cut down the connection pool.



And as a result, we can see that the
transaction rate has come back up again.



The CP utilization's come up, but the transit, the actual response time, is again



still fairly poor. It's up near to 14,
nearly a 100



milliseconds in itself. And so we still
haven't



actually solved the stability of the system.
There still



is wait events and contention going on
inside the database here at this point.



in time. It's---



it's on a latch and although the
throughput is back on the system but we



can see that the response time is still



bouncing around quite a little bit, although the CPU



is up in the ninety percent utilization.
Now the fact



that we reduce the number of connections,



what I like to think about is what
happens if we have those connection set to



2000 in the pool



and we jumped it to 6,000. At this point
in time, the system is still not ideal,



but there would have been a faction



people saying, "we need more connections." Now we show showed what happens when we



went with a high number of



connections, we just reduced it but it's
still not perfect by any stretch of the



imagination in terms of the performance.



So what we're going to start doing is
taking a little bit of computer science.



Remember when we were at school, we
learned about



time slicing and trying to schedule
multiple processes onto a CPU.



We learned very quickly that there will be a point



where if you over schedule the CPU, you would actually get a lower throughput



on the system altogether. And this is
being played out on a bigger and bigger



scale.



Now, I know I have 24 cores or 



processors on this machine that I'm
working on.



So if I was to reduce this connection,
or the number active processes



more in phase with computer science and
get it down closer to 24



or a small multiple of 24, let's



see what actually happened to the
performance and the stability of the



system.



To this point, I'm going to drop. Instead of
having over 2,000 connections in



the pool,



I'm gonna take it to 144. And let's just
apply that change.



And let's just see what actually happens
to both the throughput,



the user response time, and actually the
CPU on the system.



Well you can see we are now doing the
transition and you'll notice that



very quickly that transition and
reestablishing the connection pool



took next to no time at all. Remember how
long it took when we tried to come down from



6 thousand



to 2 thousand. It took a long time to transition across.



That drop in that connection pool down
to



144 was extremely quick. Imagine your
failover being that quick.



And now let's see what actually
has happened to the system.



It's quite dramatic. The only thing I
have changed



is the size of the connection pool. The
workload is coming at me at the same



rate.



But if we actually look and see what's
happening to the system, you'll notice



that



one, the response time now is under 10
milliseconds



time spent both in the application
server and on the database. We've got



this



huge drop down in response time.



It's much more consistent. We see
slightly more



throughput on the system, but what's more
interesting is



look at the drop in the amount of CPU



being utilized on the system. Now this is
where it becomes extremely difficult to



argue in a highly-charged escalation
meeting.



To explain to somebody you want to
reduce the number of connections



so you can reduce the amount of CPU so you can get faster response time,



and get more work through the system. At
some point in what I've just said, I



contradicted myself.



But the reality is, is we are
actually using less CPU.



We are getting higher throughput. And the
response time is less.



And half the clue is twofold---is one,



you'll notice with we're not doing any
contention events now



inside the database. So all that CPU that
we were wasting spending on latches



and arbitrating contention, is now being



redirected to actually processed
database transactions.



And the other aspect of the thing is
because we're running fewer and fewer



connections to the database,



those connections are staying on the CPU,
they are staying scheduled on the CPU for longer,



and as a result all memory pages
associated with those processes



are staying resident on the CPU cache.



And as a result, they become more and
more efficient



at scheduling and they're stalling less on
memory and as a result



we just raise the performance gain. So



just to summarize, dynamic connection
pools



are extremely dangerous because they can destabilize the system



really quickly. We showed that in slow
motion



as we incremented the workload. And 
then connection pools that are massively



oversubscribing the system by



a hundred a thousand times number of
cores on the system,



are inherently inefficient and again



can destabilize the system very quickly.

