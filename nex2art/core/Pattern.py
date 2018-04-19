import sys
import re

class Pattern(object):
    def __init__(self, limit):
        self.limit = limit

    def convert(self, regexes):
        pospats, negpats, inter, inter2 = [], [], [], []
        parser = PatternParser()
        for regex in regexes: inter.extend(parser.parseRegex(regex).convert())
        for x in inter: x.simplify()
        for y in inter:
            for x in inter:
                if x == y: continue
                if x.compare(y): break
            else:
                if y not in inter2: inter2.append(y)
        if self.limit != None:
            count = 0
            for x in inter2:
                pc, nc = x.countpatterns()
                count += pc + nc
            if self.limit < count:
                raise RuntimeError("Cannot convert, too many patterns")
        for part in inter2:
            pos, neg = part.expand()
            for p in pos:
                pat = self.makestring(self.simplify(p))
                if self.isvalid(pat): pospats.append(pat)
            for n in neg:
                pat = self.makestring(self.simplify(n))
                if self.isvalid(pat): negpats.append(pat)
        pospats = self.deduplicate(pospats)
        negpats = self.deduplicate(negpats)
        if len(pospats) <= 0:
            raise RuntimeError("Conversion failed, no valid positive patterns")
        return pospats, negpats

    def makestring(self, sequence):
        res = []
        for chunk in sequence:
            if isinstance(chunk, WildcardSeg): res.append(chunk.typ)
            elif isinstance(chunk, CharClassSeg): res.append(unichr(chunk.ranges[0]))
            else: raise RuntimeError("Cannot stringify type" + chunk.__class__.__name__)
        return unicode(''.join(res))

    def isvalid(self, pattern):
        if '//' in pattern: return False
        return True

    def deduplicate(self, patterns):
        results, splits = set(), []
        for pat in patterns: splits.append(pat.split('/'))
        for idx, subsplit in enumerate(splits):
            for supsplit in splits:
                if supsplit == subsplit: continue
                if self.ddmajor(supsplit, subsplit): break
            else: results.add(patterns[idx])
        return list(results)

    def ddmajor(self, sup, sub):
        supidx, subidx, stack = 0, 0, []
        suplen, sublen = len(sup), len(sub)
        while True:
            fail = False
            if suplen <= supidx and sublen <= subidx: return True
            elif (suplen == (supidx + 1) and sublen <= subidx and
                      sup[supidx] == '**'): return True
            elif suplen <= supidx or sublen <= subidx: fail = True
            elif sup[supidx] == '**':
                stack.append((supidx, subidx + 1))
                supidx += 1
                continue
            elif sub[subidx] == '**': fail = True
            elif not self.ddminor(sup[supidx], sub[subidx]): fail = True
            if fail and len(stack) <= 0: return False
            elif fail: supidx, subidx = stack.pop()
            else: supidx, subidx = supidx + 1, subidx + 1

    def ddminor(self, sup, sub):
        supidx, subidx, stack = 0, 0, []
        suplen, sublen = len(sup), len(sub)
        while True:
            fail = False
            if suplen <= supidx and sublen <= subidx: return True
            elif (suplen == (supidx + 1) and sublen <= subidx and
                      sup[supidx] == '*'): return True
            elif suplen <= supidx or sublen <= subidx: fail = True
            elif sup[supidx] == '*':
                stack.append((supidx, subidx + 1))
                supidx += 1
                continue
            elif sup[supidx] == '?': fail = sub[subidx] == '*'
            elif sup[supidx] != sub[subidx]: fail = True
            if fail and len(stack) <= 0: return False
            elif fail: supidx, subidx = stack.pop()
            else: supidx, subidx = supidx + 1, subidx + 1

    def simplify(self, sequence):
        def typ(i):
            if isinstance(sequence[i], WildcardSeg):
                return sequence[i].typ
            elif isinstance(sequence[i], CharClassSeg):
                return unichr(sequence[i].ranges[0])
            else: return '.'
        if len(sequence) > 0 and typ(-1) == '/': del sequence[-1]
        if len(sequence) > 0 and typ(0) == '/': del sequence[0]
        idx = 0
        while idx < len(sequence) - 1:
            tx, ty = typ(idx), typ(idx + 1)
            if tx == '*' and ty == '?':
                sequence[idx], sequence[idx + 1] = sequence[idx + 1], sequence[idx]
                idx += 1
            elif tx == '***' and ty in ('*', '***'): del sequence[idx + 1]
            elif tx == '*' and ty in ('*', '***'): del sequence[idx]
            else: idx += 1
        idx = 0
        while idx < len(sequence):
            if typ(idx) != '***':
                idx += 1
                continue
            sequence[idx] = WildcardSeg('**')
            if idx > 0 and typ(idx - 1) != '/':
                sequence.insert(idx, CharClassSeg([ord('/')]))
                sequence.insert(idx, WildcardSeg('*'))
                idx += 2
            if idx + 1 < len(sequence) and typ(idx + 1) != '/':
                sequence.insert(idx + 1, WildcardSeg('*'))
                sequence.insert(idx + 1, CharClassSeg([ord('/')]))
            idx += 1
        idx = 0
        while idx < len(sequence) - 1:
            tx, ty = typ(idx), typ(idx + 1)
            if tx == '*' and ty == '?':
                sequence[idx], sequence[idx + 1] = sequence[idx + 1], sequence[idx]
                idx += 1
            elif tx == '*' and ty == '*': del sequence[idx]
            else: idx += 1
        fseq, fx = [], []
        for seg in sequence:
            if isinstance(seg, CharClassSeg) and seg.ranges == [ord('/')]:
                fseq.append(fx)
                fx = []
            else: fx.append(seg)
        fseq.append(fx)
        idx = 0
        while idx < len(fseq) - 1:
            if len(fseq[idx]) != 1 or len(fseq[idx + 1]) != 1:
                idx += 1
                continue
            tx, ty = '.', '.'
            if isinstance(fseq[idx][0], WildcardSeg):
                tx = fseq[idx][0].typ
            if isinstance(fseq[idx + 1][0], WildcardSeg):
                ty = fseq[idx + 1][0].typ
            if tx == '**' and ty == '*':
                fseq[idx], fseq[idx + 1] = fseq[idx + 1], fseq[idx]
                idx += 1
            elif tx == '**' and ty == '**': del fseq[idx]
            else: idx += 1
        idx, wc = 0, None
        while idx < len(fseq):
            if len(fseq[idx]) != 1: break
            if not isinstance(fseq[idx][0], WildcardSeg): break
            if fseq[idx][0].typ == '*':
                idx += 1
                continue
            if fseq[idx][0].typ == '**':
                wc = fseq[idx]
                del fseq[idx]
            break
        if wc != None: fseq.insert(0, wc)
        if fseq[:1] != [[WildcardSeg('**')]]: fseq.insert(0, [])
        elif len(fseq) > 1: del fseq[0]
        if len(fseq) > 1 and fseq[-1] == [WildcardSeg('**')]: fseq[-1] = []
        res, first = [], True
        for f in fseq:
            if first: first = False
            else: res.append(CharClassSeg([ord('/')]))
            res.extend(f)
        return res

class CharClass(object):
    @staticmethod
    def unioncls(xcls, ycls):
        xl, yl = len(xcls), len(ycls)
        s, e = None, None
        x, y = 0, 0
        res = []
        while x < xl or y < yl:
            u, v = (xcls[x] if x < xl else None), (ycls[y] if y < yl else None)
            if not isinstance(u, tuple): u = u, u
            if not isinstance(v, tuple): v = v, v
            if x < xl and (y >= yl or u[0] < v[0]): k, x = u, x + 1
            else: k, y = v, y + 1
            if e == None: s, e = k
            elif k[0] <= e + 1: e = max(e, k[1])
            else:
                res.append(s if s == e else (s, e))
                s, e = k
        if e != None: res.append(s if s == e else (s, e))
        return res

    @staticmethod
    def intersectcls(xcls, ycls):
        xl, yl = len(xcls), len(ycls)
        x, y = 0, 0
        res = []
        while x < xl and y < yl:
            u, v = xcls[x], ycls[y]
            if not isinstance(u, tuple): u = u, u
            if not isinstance(v, tuple): v = v, v
            if u[1] < v[1]: x += 1
            else: y += 1
            k = max(u[0], v[0]), min(u[1], v[1])
            if k[0] <= k[1]: res.append(k[0] if k[0] == k[1] else k)
        return res

    @staticmethod
    def invertcls(ccls):
        e = 0
        res = []
        for c in ccls:
            ks, ke = c if isinstance(c, tuple) else (c, c)
            ks, ke = ks - 1, ke + 1
            if ks == e: res.append(ks)
            elif ks > e: res.append((e, ks))
            e = ke
        ks = sys.maxunicode
        if ks == e: res.append(ks)
        elif ks > e: res.append((e, ks))
        return res

    @staticmethod
    def countcls(ccls):
        ct = 0
        for c in ccls:
            if isinstance(c, tuple): ct += 1 + c[1] - c[0]
            else: ct += 1
        return ct

    @staticmethod
    def expand(ccls):
        for c in ccls:
            if isinstance(c, tuple):
                for k in xrange(c[0], c[1] + 1): yield k
            else: yield c

class PatternSeg(object):
    def __init__(self):
        pass

    def __repr__(self):
        if len(vars(self)) <= 0: return '{' + self.__class__.__name__ + '}'
        return '{' + self.__class__.__name__ + ' ' + repr(vars(self))[1:]

    def __eq__(self, other):
        if self.__class__ is not other.__class__: return False
        if vars(self) != vars(other): return False
        return True

    def countpatterns(self):
        return 1, 0

    def expand(self):
        return [[self]], []

    def compare(self, other):
        msg = "Cannot compare pattern type "
        raise RuntimeError(msg + self.__class__.__name__)

    def simplify(self):
        return

class EmptySeg(PatternSeg):
    def __init__(self):
        pass

class CharClassSeg(PatternSeg):
    def __init__(self, ranges):
        self.ranges = ranges

    def countpatterns(self):
        posct = CharClass.countcls(self.ranges)
        negct = CharClass.countcls(CharClass.invertcls(self.ranges))
        if posct <= negct: return posct, 0
        elif len(CharClass.intersectcls(self.ranges, [ord('/')])) <= 0:
            return 1, negct - 1
        else: return 2, negct

    def expand(self):
        posct = CharClass.countcls(self.ranges)
        negct = CharClass.countcls(CharClass.invertcls(self.ranges))
        if posct <= negct:
            chars = []
            for char in CharClass.expand(self.ranges):
                chars.append([CharClassSeg([char])])
            return chars, []
        elif len(CharClass.intersectcls(self.ranges, [ord('/')])) <= 0:
            chars = []
            for char in CharClass.expand(CharClass.invertcls(self.ranges)):
                if char != ord('/'): chars.append([CharClassSeg([char])])
            return [[WildcardSeg('?')]], chars
        else:
            chars = []
            for char in CharClass.expand(CharClass.invertcls(self.ranges)):
                chars.append([CharClassSeg([char])])
            return [[CharClassSeg([ord('/')])], [WildcardSeg('?')]], chars

    def compare(self, other):
        if not isinstance(other, CharClassSeg): return False
        return self.ranges == CharClass.unioncls(self.ranges, other.ranges)

class BackreferenceSeg(PatternSeg):
    def __init__(self, idx):
        self.idx = idx

class WildcardSeg(PatternSeg):
    def __init__(self, typ):
        self.typ = typ

    def compare(self, other):
        if isinstance(other, WildcardSeg):
            if self.typ == '***': return True
            elif self.typ == '*' and other.typ == '*': return True
            else: return False
        elif isinstance(other, CharClassSeg):
            if self.typ == '***': return True
            elif self.typ == '*':
                return len(CharClass.intersectcls(other.ranges, [ord('/')])) <= 0
        else: return False

class BoundarySeg(PatternSeg):
    def __init__(self, typ):
        self.typ = typ

class GroupSeg(PatternSeg):
    def __init__(self, idx, name, elems):
        self.idx = idx
        self.name = name
        self.elems = elems

    def countpatterns(self):
        posct, negct = 1, 0
        for elem in self.elems:
            p, n = elem.countpatterns()
            posct *= p
            negct += n
        return posct, posct*negct

    def expand(self):
        popts, nopts = [[]], []
        for elem in self.elems:
            xpopts, xnopts = [], []
            pos, neg = elem.expand()
            for opt in pos:
                for xopt in popts: xpopts.append(xopt + opt)
                for xopt in nopts: xnopts.append(xopt + opt)
            for opt in neg:
                for xopt in popts: xnopts.append(xopt + opt)
            popts, nopts = xpopts, xnopts
        return popts, nopts

    def compare(self, other):
        if not isinstance(other, GroupSeg): return False
        sup, sub = self.elems, other.elems
        supidx, subidx, stack = 0, 0, []
        suplen, sublen = len(sup), len(sub)
        while True:
            fail = False
            if suplen <= supidx and sublen <= subidx: return True
            elif (suplen == (supidx + 1) and sublen <= subidx and
                      isinstance(sup[supidx], WildcardSeg)): return True
            elif suplen <= supidx or sublen <= subidx: fail = True
            elif isinstance(sup[supidx], WildcardSeg):
                if sup[supidx].compare(sub[subidx]):
                    stack.append((supidx, subidx + 1))
                supidx += 1
                continue
            elif not sup[supidx].compare(sub[subidx]): fail = True
            if fail and len(stack) <= 0: return False
            elif fail: supidx, subidx = stack.pop()
            else: supidx, subidx = supidx + 1, subidx + 1

    def simplify(self):
        def typ(i):
            if isinstance(self.elems[i], WildcardSeg): return self.elems[i].typ
            else: return None
        idx = 0
        while idx < len(self.elems) - 1:
            tx, ty = typ(idx), typ(idx + 1)
            if tx == '***' and ty in ('*', '***'): del self.elems[idx + 1]
            elif tx == '*' and ty in ('*', '***'): del self.elems[idx]
            else: idx += 1

class LookaroundSeg(PatternSeg):
    def __init__(self, typ, elems):
        self.typ = typ
        self.elems = elems

class Element(object):
    def __init__(self):
        pass

    def __repr__(self):
        if len(vars(self)) <= 0: return '{' + self.__class__.__name__ + '}'
        return '{' + self.__class__.__name__ + ' ' + repr(vars(self))[1:]

class CharLiteral(Element):
    def __init__(self, char):
        self.char = char

    def convert(self):
        return [CharClassSeg([ord(self.char)])]

class SimpleCharClass(Element):
    def __init__(self, typ):
        self.typ = typ

    def convert(self):
        t = self.typ.lower()
        if t == '.': s = [(0, sys.maxunicode)]
        elif t == 'd': s = [(ord('0'), ord('9'))]
        elif t == 's': s = [ord(' '), ord('\t'), ord('\r'), ord('\n'), ord('\f'), ord('\x0B')]
        elif t == 'w': s = [(ord('0'), ord('9')), (ord('A'), ord('Z')), ord('_'), (ord('a'), ord('z'))]
        else: raise RuntimeError("Invalid regex char class " + self.typ)
        if self.typ.isupper(): s = CharClass.invertcls(s)
        return [CharClassSeg(s)]

class NamedCharClass(Element):
    def __init__(self, name, neg):
        self.name = name
        self.neg = neg

    def convert(self):
        # TODO
        raise RuntimeError("Named char classes are not yet supported")

class CustomCharClass(Element):
    def __init__(self, neg, elems):
        self.neg = neg
        self.elems = elems

    def convert(self):
        ranges = [(0, sys.maxunicode)]
        for chunk in self.elems:
            cranges = []
            for ccls in chunk:
                c = ccls.convert()
                if len(c) != 1 or not isinstance(c[0], CharClassSeg):
                    raise RuntimeError("Non-class cannot be inside class")
                cranges = CharClass.unioncls(cranges, c[0].ranges)
            ranges = CharClass.intersectcls(ranges, cranges)
        if self.neg: ranges = CharClass.invertcls(ranges)
        return [CharClassSeg(ranges)]

class CharRange(Element):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def convert(self):
        return [CharClassSeg([(ord(self.start), ord(self.end))])]

class Backreference(Element):
    def __init__(self, ident):
        self.ident = ident

    def convert(self):
        # TODO
        raise RuntimeError("Backreferences are not yet supported")

class Quantifier(Element):
    def __init__(self, start, end, strat, elem):
        self.start = start
        self.end = end
        self.strat = strat
        self.elem = elem

    def convert(self):
        start, end = self.start, self.end
        unbound = end == None
        if unbound: end = start
        elem = self.elem.convert()
        wildcard = None
        if unbound:
            wildcard = False
            if len(elem) == 1 and isinstance(elem[0], CharClassSeg):
                revcls = CharClass.invertcls(elem[0].ranges)
                if len(revcls) == 0:
                    wildcard = [[WildcardSeg('*')], [WildcardSeg('***')]]
                elif len(revcls) == 1 and revcls[0] == ord('/'):
                    wildcard = [[WildcardSeg('*')]]
        if wildcard == False:
            raise RuntimeError("Cannot convert complex expression to wildcard")
        chunks = []
        for i in xrange(start, end + 1):
            chunk = []
            for j in xrange(i): chunk.append(self.elem)
            chunks.append(chunk)
        opts = Group('ng', chunks).convert()
        nopts = []
        if unbound:
            for opt in opts:
                if not isinstance(opt, GroupSeg):
                    for choice in wildcard:
                        nopts.append(GroupSeg(None, None, [opt] + choice))
                else:
                    for choice in wildcard:
                        nopts.append(GroupSeg(None, None, opt.elems + choice))
            return nopts
        return opts

class Boundary(Element):
    def __init__(self, ident):
        self.ident = ident

    def convert(self):
        # TODO
        raise RuntimeError("Boundaries are not yet supported")

class Group(Element):
    def __init__(self, typ, elems, num=None, name=None, flags=None):
        self.typ = typ
        self.num = num
        self.name = name
        self.flags = flags
        self.elems = elems

    def convert(self):
        # TODO
        if self.typ != None and self.typ[1] == 'l':
            raise RuntimeError("Lookarounds are not yet supported")
        opts = []
        for chunks in self.elems:
            copts = [[]]
            for chunk in chunks:
                xopts = []
                for opt in chunk.convert():
                    if isinstance(opt, GroupSeg): elem = opt.elems
                    else: elem = [opt]
                    for pref in copts: xopts.append(pref + elem)
                copts = xopts
            opts.extend(copts)
        realopts, clsopts, clsp = [], [], False
        for opt in opts:
            opt = filter(lambda x: not isinstance(x, EmptySeg), opt)
            if len(opt) == 1 and isinstance(opt[0], CharClassSeg):
                clsp = True
                clsopts = CharClass.unioncls(clsopts, opt[0].ranges)
            elif len(opt) == 1:
                realopts.append(opt[0])
            elif len(opt) <= 0:
                realopts.append(EmptySeg())
            elif len(opt) > 1:
                realopts.append(GroupSeg(self.num, self.name, opt))
        if clsp: realopts.append(CharClassSeg(clsopts))
        return realopts

class PatternParser(object):
    def __init__(self):
        self.groupct = None
        self.octl = re.compile(r'\\0([0-7][0-7]?|[0-3][0-7][0-7])')
        self.hexu = re.compile(r'\\u([0-9a-fA-F]{4})')
        self.hexl = re.compile(r'\\x([0-9a-fA-F]{2})')
        self.hexg = re.compile(r'\\x\{([0-9a-fA-F]+)\}')
        self.ctrl = re.compile(r'\\c([A-Z\[\]\\@^_?])')
        self.ccls = re.compile(r'\\([pP])\{([a-zA-Z=_]+)\}')
        self.nref = re.compile(r'\\k<([a-zA-Z][a-zA-Z0-9]*)>')
        self.bref = re.compile(r'\\([1-9][0-9]*)')
        self.cesc = re.compile(r'\\(.)')
        self.fcls = re.compile(r'\[(\^)?')
        self.isec = re.compile(r'\&\&')
        self.qunt = re.compile(r'(?:([?*+])|\{([0-9]+)(,([0-9]+)?)?\})([?+])?')
        self.flag = re.compile(r'\(\?([idmsuxU]+)?(?:-([idmsuxU]+))?\)')
        self.fgrp = re.compile(r'\(\?([idmsux]+)?(?:-([idmsux]+))?:')
        self.ngrp = re.compile(r'\(\?<([a-zA-Z][a-zA-Z0-9]*)>')
        self.pgrp = re.compile(r'\((?:\?(=|!|<=|<!|>))?')
        self.errs = re.compile(r'[(){\[\\?*+]')
        self.errc = re.compile(r'[\[\\]')
        self.litr = re.compile(r'.')
        self.gmatch = [
            self.octl, self.hexu, self.hexl, self.hexg, self.ctrl, self.ccls,
            self.nref, self.bref, self.cesc, self.fcls, self.qunt, self.flag,
            self.fgrp, self.ngrp, self.pgrp, self.errs, self.litr]
        self.cmatch = [
            self.octl, self.hexu, self.hexl, self.hexg, self.ctrl, self.ccls,
            self.cesc, self.fcls, self.isec, self.errc, self.litr]

    def parseRegex(self, pat):
        self.groupct = 0
        result, _ = self.parseGroup(None, None, None, pat, 0)
        return result

    def parseGroup(self, typ, name, flags, pat, idx):
        gidx = None
        if typ != None and typ[0] == 'c':
            self.groupct += 1
            gidx = self.groupct
        chunks, currchunk = [], []
        while True:
            if typ == None and len(pat) == idx:
                if len(currchunk) > 0: chunks.append(currchunk)
                return Group(None, chunks), idx
            insrt = None
            match, idx = self.match(pat, idx, self.gmatch)
            if typ != None and match.re == self.errs and match.group() == ')':
                if len(currchunk) > 0: chunks.append(currchunk)
                return Group(typ, chunks, gidx, name, flags), idx
            elif match.re == self.litr and match.group() == '|':
                if len(currchunk) > 0:
                    chunks.append(currchunk)
                    currchunk = []
            elif match.re == self.cesc and match.group(1) == 'Q':
                quoted, idx = self.parseQuoted(pat, idx)
                currchunk.extend(quoted)
            elif match.re == self.fcls:
                insrt, idx = self.parseClass(match.group(1) != None, pat, idx)
            elif match.re == self.fgrp:
                pfs = match.group(1)
                nfs = match.group(2)
                if pfs == None and nfs == None: fs = None
                elif pfs == None: fs = '-' + nfs
                elif nfs == None: fs = pfs
                else: fs = pfs + '-' + nfs
                insrt, idx = self.parseGroup('ng', None, fs, pat, idx)
            elif match.re == self.ngrp:
                nm = match.group(1)
                insrt, idx = self.parseGroup('cg', nm, None, pat, idx)
            elif match.re == self.pgrp:
                rs = match.group(1)
                if rs == None: tp = 'cg'
                elif rs == '>': tp = 'ni'
                elif rs == '=': tp = 'nlap'
                elif rs == '!': tp = 'nlan'
                elif rs == '<=': tp = 'nlbp'
                elif rs == '<!': tp = 'nlbn'
                insrt, idx = self.parseGroup(tp, None, None, pat, idx)
            elif match.re == self.qunt:
                if len(currchunk) <= 0:
                    raise RuntimeError("Regex parse error: Dangling quantifier")
                simp = match.group(1)
                start = match.group(2)
                rang = match.group(3)
                end = match.group(4)
                strat = match.group(5)
                if simp == None:
                    start = int(start)
                    if rang == None: end = start
                    elif end != None: end = int(end)
                elif simp == '?': start, end = 0, 1
                elif simp == '*': start, end = 0, None
                elif simp == '+': start, end = 1, None
                insrt = Quantifier(start, end, strat, currchunk[-1])
                del currchunk[-1]
            else: insrt = self.parseSimpleMatch(match)
            if insrt != None: currchunk.append(insrt)

    def parseClass(self, neg, pat, idx):
        chunks, currchunk = [], []
        while True:
            insrt = None
            match, idx = self.match(pat, idx, self.cmatch)
            if match.re == self.litr and match.group() == ']':
                if len(currchunk) > 0: chunks.append(currchunk)
                return CustomCharClass(neg, chunks), idx
            elif match.re == self.litr and match.group() in '.^$':
                insrt = CharLiteral(match.group())
            elif match.re == self.cesc and match.group(1) == 'Q':
                quoted, idx = self.parseQuoted(pat, idx)
                currchunk.extend(quoted)
            elif match.re == self.isec:
                if len(currchunk) > 0:
                    chunks.append(currchunk)
                    currchunk = []
            elif match.re == self.fcls:
                insrt, idx = self.parseClass(match.group(1) != None, pat, idx)
            else: insrt = self.parseSimpleMatch(match)
            if insrt != None:
                if isinstance(insrt, Boundary):
                    raise RuntimeError("Regex parse error: invalid escape sequence \\" + insrt.ident)
                if len(currchunk) > 1:
                    q1 = isinstance(insrt, CharLiteral)
                    q2 = isinstance(currchunk[-1], CharLiteral)
                    q3 = isinstance(currchunk[-2], CharLiteral)
                    if (q1 and q2 and q3 and currchunk[-1].char == '-'):
                        insrt = CharRange(currchunk[-2].char, insrt.char)
                        del currchunk[-2:]
                currchunk.append(insrt)

    def match(self, pat, idx, matchlist):
        for matcher in matchlist:
            match = matcher.match(pat, idx)
            if match != None: return match, match.end()

    def parseQuoted(self, pat, idx):
        quoted = []
        while len(pat) > idx:
            if pat[idx:idx + 2] == '\\E': return quoted, idx + 2
            quoted.append(CharLiteral(pat[idx]))
            idx += 1
        return quoted, idx

    def parseSimpleMatch(self, match):
        if match.re == self.octl:
            return CharLiteral(unichr(int(match.group(1), 8)))
        elif match.re == self.hexu or match.re == self.hexl or match.re == self.hexg:
            return CharLiteral(unichr(int(match.group(1), 16)))
        elif match.re == self.ctrl:
            ch = ord(match.group(1))
            if ch < 64: ch += 64
            else: ch -= 64
            return CharLiteral(unichr(ch))
        elif match.re == self.ccls:
            return NamedCharClass(match.group(2), match.group(1) == 'P')
        elif match.re == self.nref:
            return Backreference(match.group(1))
        elif match.re == self.bref:
            return Backreference(int(match.group(1)))
        elif match.re == self.cesc:
            ch = match.group(1)
            if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9':
                if ch == 'e': return CharLiteral('\x1b')
                elif ch in 'tnrfa': return CharLiteral(('\\' + ch).decode('string_escape'))
                elif ch in 'dDsSwW': return SimpleCharClass(ch)
                elif ch in 'bBAGZz': return Boundary(ch)
                else: raise RuntimeError("Regex parse error: invalid escape sequence \\" + ch)
            else: return CharLiteral(ch)
        elif match.re == self.flag:
            pfs = match.group(1)
            nfs = match.group(2)
            if pfs == None and nfs == None: fs = None
            elif pfs == None: fs = '-' + nfs
            elif nfs == None: fs = pfs
            else: fs = pfs + '-' + nfs
            return Group('nf', None, flags=fs)
        elif match.re == self.litr:
            ch = match.group()
            if ch == '.': return SimpleCharClass(ch)
            elif ch in '^$': return Boundary(ch)
            else: return CharLiteral(ch)
        else:
            ch = "'" + match.group() + "'"
            raise RuntimeError("Regex parse error: invalid character " + ch)
