

dict = {
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
        "<a href='http://clang.llvm.org/' >clang</a>",
    "julia" :
        "<a href='http://julialang.org/' >Julia</a>",
    "aws" :
        "<a href='http://aws.amazon.com/' >Amazon Web Service</a>"
}

def replace(s):
    return reduce(lambda x, y: x.replace(y, dict[y]), dict, s)