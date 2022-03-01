DIR=$(realpath $(dirname $0))
mkdir -p $DIR/jacarte.github.io
git clone https://github.com/Jacarte/jacarte.github.io.git $DIR/jacarte.github.io
cp $1 $DIR/Lic.pdf


python3 $DIR/split_document.py 

mkdir -p $DIR/jacarte.github.io/assets/pdf/thesis/
cp $DIR/chapter* $DIR/jacarte.github.io/assets/pdf/thesis/

CW=$PWD
cd $DIR/jacarte.github.io
git add assets/pdf/thesis/
git commit -m "Thesis update"
git push

./bin/deploy


cd $CW
#rm $DIR/*.pdf
# Copy the chapters individually
