class @Videoplayer
  constructor: (@directory, @url, @clip, @chapters) ->
    @active_chapter = -1
    @loaded = false
    @loading = false
    $("#flowplayer_controls_play").click =>
      @load(0)
    #@prev = $("#flowplayer_controls_play")
  
  load: (chapter=0) ->
    $f "flowplayer_invisible", @directory + 'flowplayer-3.2.16.swf',
      debug: false
      clip:
        url: @clip
        debug: false
        provider: 'rtmp'
        autoPlay: true
        autoBuffering: true
        onStart: =>
          @loaded = true      
          @setState("active")
          @seekToChapter(chapter)
      plugins:
        rtmp:
          url: @directory + 'flowplayer.rtmp-3.2.12.swf'
          netConnectionUrl: @url
    
  setState: (state) ->
    console.log("setting to: " + state ) 
      
  seekToChapter: (chapter) ->
    console.log("seeking to chapter: " + chapter)
    
    
    
#       $f("flowplayer_invisible", media_url + "slidecasting-media/flowplayer/flowplayer-3.2.16.swf", {
#           debug: false,
#           clip: {
#               url: videoclip_name_local,
#               debug: false,
#               provider: 'rtmp',
#               autoPlay: true,
#               autoBuffering: true,
#               onStart: function(){
#                   setPlayerControlState("active");
#                   videoclip_loaded = true;
#                   seekToChapter(videoclip_chapter_local);
#                   this.setVolume(100);
#                   this.unmute();
#               },
#               onCuepoint:[videoclip_chapters, function(clip, cuepoint){
#                   arrivedAtCuepoint(clip, cuepoint);
#               }]
#           },
#           plugins: {
#               rtmp: {
#                   url: media_url + "slidecasting-media/flowplayer/flowplayer.rtmp-3.2.12.swf",
#                   netConnectionUrl: videoclip_url_local //"rtmp://video.zserv.tuwien.ac.at/lecturetube_public" 
#               }
#           },
#           onError: function(){
#               setPlayerControlState("error");
#           }
#       });
#   }