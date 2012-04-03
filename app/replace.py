

dict = {
    'Xingzhong' : 
        "<a href='http://www.sirxu.com' >Xingzhong</a>",
    "Prof. Hong Man" : 
        "<a href='http://www.ece.stevens-tech.edu/~hman/' >Prof. Hong Man</a>",
    "Stevens Institute of Technology" : 
        "<a href='http://www.stevens.edu' >Stevens Institute of Technology</a>",
    "Beijing Jiaotong University" : 
        "<a href='http://www.bjtu.edu.cn' >Beijing Jiaotong University</a>",
    "Google App Engine" :
        "<a href='https://developers.google.com/appengine/' >Google App Engine</a>",
    "GNU-Radio" :
        "<a href='http://gnuradio.org/' >GNU-Radio</a>",
    "clang" :
        "<a href='http://clang.llvm.org/' >clang</a>"
}

def replace(s):
    return reduce(lambda x, y: x.replace(y, dict[y]), dict, s)