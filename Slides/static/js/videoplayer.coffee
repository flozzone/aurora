class @Videoplayer
  constructor: (@player, @url, @clip, @chapters) ->
    console.log @player
  
  load: ->
    console.log("loading")
    $f("flowplayer_invisible", @player)
    
    
    
    
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