class ConvertNumberToString:
    keys = [1000000000000000, 1000000000000, 1000000000, 1000000, 1000, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    values = ["квадриллион", "триллион", "миллиард", "миллион", "миң", "жүз", "токсон", "сексен", "жетимиш", "алтымыш", "элүү", "кырк", "отуз", "жыйырма", "он", "тогуз", "сегиз", "жети", "алты",
          "беш", "төрт", "үч", "эки", "бир"]
    def convert(self, n, l, r):
        n = int(n)
        for i in self.keys:
            t = n // i
            if t >= 1:
                if t in self.keys:
                    if t > 1:
                        r += " "+self.values[self.keys.index(t)]+" "+self.values[self.keys.index(i)]
                    else:
                        r += " " + self.values[self.keys.index(i)]
                else:
                    r = self.convert(t, self.values[self.keys.index(i)], r)
                n %= i
        return r + " " + l
