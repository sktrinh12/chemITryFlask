function Ellipsis(x,y,r_a,r_b) {

    this.x = x;
    this.y = y;
    this.r_a = r_a;
    this.r_b = r_b;
    var cnt = 0;

    this.dots = function(adder) {
      strokeWeight(2);
      this.xCtr = this.x;
      this.yCtr = this.y;
      this.adder = adder;

      // let theta = acos(cnt/this.r_a);
      let xPos = this.xCtr - (this.r_a/2 * cos(cnt));
      let yPos = this.yCtr - (this.r_b/2 * sin(cnt));
      ellipse(xPos,yPos,20,20)
      cnt = cnt + this.adder; 
      // console.log(`deg: ${deg}, cnt: ${cnt}`);
    }

    this.show = function(thickness) {
      this.thickness = thickness;
      noFill();
      strokeWeight(this.thickness);
      ellipse(this.x, this.y, this.r_a, this.r_b);
    }

}


