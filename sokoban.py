import bdd;
import itertools;

import argparse;
import time;

"""
NOTE: This model implements a simplified version of Sokoban, which does not
take into account the reachability of boxes by the player.
"""

class Field:
    NONE  = " ";
    FLOOR = ".";
    BOX   = "x";
    GOAL  = "o";
    MAN   = "@";

class Sokoban(object):
    """
    Sokoban object.
    """
    # initial board layout
    # Sokoban levels (c) 1982 Thinking Rabbit
    levels = [
        # Level 1
        ["    ...             ",
         "    x..             ",
         "    ..x             ",
         "  ..x..x.           ",
         "  . .   .           ",
         "... .   .       ..oo",
         ".x..x.............oo",
         "    .    . @    ..oo",
         "    ......          "],
        # Level 2
        ["oo.. .....  ",
         "oo.. .x..x..",
         "oo.. x    ..",
         "oo....@.  ..",
         "oo.. . ..x. ",
         "     .  x.x.",
         "  .x..x.x.x.",
         "  .... ....."],
        # Level 3
        ["        .....@ ",
         "        .x x.  ",
         "        .x..x  ",
         "         x.x.  ",
         "        .x. .  ",
         "oooo..  .x..x..",
         " ooo....x..x...",
         "oooo..         "],
    ];

    def __init__(self, level=1):
        dd = bdd.BDD();
        self.bdd = dd;
        self._var = 0;

        self.layout = self.levels[level - 1];

        lay = self.layout;
        self.rows, self.cols = len(lay), len(lay[0]);

        R, C = self.rows, self.cols;

        self.initial = dd.true;
        self.varsSrc = bdd.BDDSet(dd);
        self.varsDst = bdd.BDDSet(dd);

        # create variables for each field and set up initial board
        self.varMap = {};
        self.playerCoord = None;
        for r, c in itertools.product(range(R), range(C)):
            if(lay[r][c]==Field.NONE):
                continue;

            # create variable pair for this field
            src, dst = self.var();
            self.varMap[(r, c)] = src;

            # add to initial board
            v = dd.var(src);
            if(lay[r][c]!=Field.BOX):
                v = ~v;
            self.initial &= v;


        # create triples of fields
        triples = [];
        for r, c in itertools.product(range(R), range(C)):
            if(lay[r][c]==Field.NONE):
                continue;

            # horizontal triple
            if((c + 2) < C
                and (lay[r][c + 1]!=Field.NONE)
                and (lay[r][c + 2]!=Field.NONE)):
                tri = bdd.BDDSet(dd);

                tri.add(self.varMap[(r, c + 0)]);
                tri.add(self.varMap[(r, c + 1)]);
                tri.add(self.varMap[(r, c + 2)]);

                triples.append(tri);

            # vertical triple
            if((r + 2) < R
                and (lay[r + 1][c]!=Field.NONE)
                and (lay[r + 2][c]!=Field.NONE)):
                tri = bdd.BDDSet(dd);

                tri.add(self.varMap[(r + 0, c)]);
                tri.add(self.varMap[(r + 1, c)]);
                tri.add(self.varMap[(r + 2, c)]);

                triples.append(tri);

        # create winning board
        self.winning = dd.false;
        """
        TODO (Sokoban lab): Construct the BDD of the winning board.
        """
        self.win_board = dd.true;
        for r, c in itertools.product(range(R), range(C)):
            if(lay[r][c]==Field.NONE):
                continue;

            # add to final board
            v = dd.var(self.varMap[(r, c)]);
            if(lay[r][c]!=Field.GOAL):
                v = ~v;
            self.win_board &= v;
        
        self.winning |= self.win_board

        # create move relation
        parts = [];
        for tri in triples:
            vars = bdd.BDDSet(dd);
            for v in tri:
                # add both source and destination vars
                vars.add(v);
                vars.add(v + 1);

            src = [dd.var(v + 0) for v in tri];
            dst = [dd.var(v + 1) for v in tri];

            rel = dd.false;
            """
            TODO (Sokoban lab): Construct the partial move relation.
            """
            pre  =  src[1] & ~src[0] & ~src[2]
            post = ~dst[1] & (dst[0] ^ dst[2])
            rel |= (pre & post)

            parts.append((rel, vars));

        self.movePartial = parts;

        self.move = dd.false;
        self.vars = self.varsSrc.union(self.varsDst);
        for rel, vars in parts:
            # keep all unaffected variables equal
            for v in self.varsSrc:
                if(v in vars):
                    continue;

                a = dd.var(v);
                b = dd.var(v + 1);
                rel &= ~(a ^ b);

            # combine partial relations
            self.move |= rel;

    def var(self):
        """
        Returns a new source/destination variable pair.
        """
        src = self._var;
        self._var += 1;
        dst = self._var;
        self._var += 1;

        self.varsSrc.add(src);
        self.varsDst.add(dst);

        return (src, dst);

    def draw(self, board):
        """
        Returns a textual representation of the given Sokoban board given
         by the evaluation [board].
        """
        R, C = self.rows, self.cols;
        lay = self.layout;

        # serialize board
        s = [[Field.NONE for _ in range(C)] for _ in range(R)];
        for r, c in itertools.product(range(R), range(C)):
            v = self.varMap.get((r, c), None);
            if(v is None):
                continue;

            if(board[v]):
                s[r][c] = Field.BOX;
            elif(lay[r][c]==Field.GOAL):
                s[r][c] = Field.GOAL;
            else:
                s[r][c] = Field.FLOOR;

        return "\n".join(["".join(i) for i in s]);

    class Stats(object):
        def __init__(self):
            self.it = 0;
            self.maxNodes = 0;

        def update(self, dd):
            n = dd.nodeCount;
            self.it += 1;
            self.maxNodes = max(self.maxNodes, n);
            print("iteration %3d: %6d nodes, %6d peak"
                   % (self.it, n, self.maxNodes), end="\r");

    def reachBFS(self):
        """
        Returns a BDD representing all reachable states,
         using the BFS algorithm.
        """
        stats = self.Stats();
        # TODO (Sokoban lab): Implement this algorithm.
        visited = self.initial
        prev = self.bdd.false
        while not (prev == visited):
            prev = visited
            visited |= visited.image(self.move, self.vars)
            stats.update(visited)
        return visited
    
    def reachBFSPart(self):
        """
        Returns a BDD representing all reachable states,
         using the BFS algorithm.
        """
        stats = self.Stats();
        # TODO (Sokoban lab): Implement this algorithm.
        visited = self.initial
        prev = self.bdd.false
        while not (prev == visited):
            prev = visited
            for rel, vars in self.movePartial:
                visited |= prev.image(rel, vars)
                stats.update(visited)
        return visited

    def reachChaining(self):
        """
        Returns a BDD representing all reachable states,
         using the chaining algorithm.
        """
        stats = self.Stats();
        # TODO (Sokoban lab): Implement this algorithm.
        visited = self.initial
        prev = self.bdd.false
        while not (prev == visited):
            prev = visited
            for rel, vars in self.movePartial:
                visited |= visited.image(rel, vars)
                stats.update(visited)
        return visited

    def reachSatLike(self):
        """
        Returns a BDD representing all reachable states,
         using a saturation-like algorithm.
        """
        stats = self.Stats();
        # TODO (Sokoban lab): Implement this algorithm.
        visited = self.initial
        prev = self.bdd.false
        while not (prev == visited):
            prev = visited
            for rel, vars in self.movePartial:
                par_prev = self.bdd.false
                while not (par_prev == visited):
                    par_prev = visited
                    visited |= visited.image(rel, vars)
                    stats.update(visited)
        return visited

    def reachSat(self):
        """
        Returns a BDD representing all reachable states,
         using the saturation algorithm.
        """
        stats = self.Stats();
        # TODO (Sokoban lab): Implement this algorithm.
        visited = self.initial
        relations: list[tuple] = []
        for r, v in self.movePartial:
            relations = relations +[(r, v)]
            prev = self.bdd.false
            while not (prev == visited):
                prev = visited
                for rel, vars in relations:
                    visited |= visited.image(rel, vars)
                    stats.update(visited)
        return visited

    reach = [
        reachBFS,
        reachBFSPart,
        reachChaining,
        reachSatLike,
        reachSat,
    ];

def main():
    """
    Perform reachability analysis on Sokoban and print winnable states.
    """
    modes = {m.__name__[5:].lower(): m for m in Sokoban.reach};

    ap = argparse.ArgumentParser(description=main.__doc__);
    ap.add_argument("--mode", choices=modes, required=True);
    ap.add_argument("--level", type=int, default=1);
    args = ap.parse_args();

    # activate requested reachability function
    soko = Sokoban(level=args.level);
    print("Sokoban level %d" % args.level);

    t0 = time.time();
    reach = modes[args.mode](soko);
    t1 = time.time();
    dt = divmod(t1 - t0, 60);

    print("\n%02d:%06.3f elapsed; %d reachable states"
           % (dt[0], dt[1], reach.pathCount));

    # print boards
    reach &= soko.winning;
    print("%d winning states" % reach.pathCount);
    for i in reach.evaluations(soko.varsSrc):
        print([int(v) for v in i if i[v]]);
        print(soko.draw(i));
        print();

if(__name__=="__main__"):
    main();
